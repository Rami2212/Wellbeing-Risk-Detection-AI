from __future__ import annotations

from dataclasses import dataclass
import logging
import pandas as pd

from .data_loader import DataLoader
from .features import build_citizen_features
from .model import RiskModel
from .langfuse_utils import observe_step, TraceClient, bind_session_to_current_trace
from .openrouter_client import OpenRouterDecisionClient

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    session_id: str
    trace_client: TraceClient


class DataIngestionAgent:
    @observe_step(name="data_ingestion_agent")
    def run(self, loader: DataLoader, context: AgentContext) -> dict[str, pd.DataFrame]:
        bind_session_to_current_trace(context.session_id)
        status = loader.load_status()
        users = loader.load_users()
        locations = loader.load_locations()
        context.trace_client.event(
            name="ingestion_summary",
            output_payload={
                "session_id": context.session_id,
                "status_rows": len(status),
                "users": len(users),
                "location_rows": len(locations),
            },
        )
        return {"status": status, "users": users, "locations": locations}


class FeatureAgent:
    @observe_step(name="feature_agent")
    def run(self, data: dict[str, pd.DataFrame], context: AgentContext) -> pd.DataFrame:
        bind_session_to_current_trace(context.session_id)
        feature_df = build_citizen_features(data["status"], data["locations"], data["users"])
        context.trace_client.event(
            name="feature_summary",
            output_payload={
                "session_id": context.session_id,
                "rows": len(feature_df),
                "columns": list(feature_df.columns),
            },
        )
        return feature_df


class MLRiskAgent:
    def __init__(self, random_state: int, contamination: float) -> None:
        self.model = RiskModel(random_state=random_state, contamination=contamination)

    @observe_step(name="ml_risk_agent")
    def run(self, feature_df: pd.DataFrame, context: AgentContext) -> pd.DataFrame:
        bind_session_to_current_trace(context.session_id)
        self.model.fit(feature_df)
        scores = self.model.score(feature_df)
        context.trace_client.event(
            name="ml_scoring",
            output_payload={
                "session_id": context.session_id,
                "max_ml_risk": float(scores["ml_risk_score"].max()),
                "min_ml_risk": float(scores["ml_risk_score"].min()),
            },
        )
        return scores


class RuleRiskAgent:
    @observe_step(name="rule_risk_agent")
    def run(self, feature_df: pd.DataFrame, context: AgentContext) -> pd.DataFrame:
        bind_session_to_current_trace(context.session_id)
        scored = pd.DataFrame({"CitizenID": feature_df["CitizenID"].to_numpy()})
        rule_score = (
            (feature_df["sleep_slope"] < -1.5).astype(int)
            + (feature_df["activity_slope"] < -1.5).astype(int)
            + (feature_df["max_exposure"] >= 70).astype(int)
            + (feature_df["min_sleep"] <= 35).astype(int)
        )
        scored["rule_risk_score"] = rule_score
        scored["rule_flag"] = (rule_score >= 2).astype(int)
        context.trace_client.event(
            name="rule_scoring",
            output_payload={
                "session_id": context.session_id,
                "rule_flags": int(scored["rule_flag"].sum()),
            },
        )
        return scored


class DecisionAgent:
    def __init__(self, openrouter_client: OpenRouterDecisionClient | None = None) -> None:
        self.openrouter_client = openrouter_client

    @observe_step(name="decision_agent")
    def run(self, ml_df: pd.DataFrame, rule_df: pd.DataFrame, context: AgentContext) -> pd.DataFrame:
        bind_session_to_current_trace(context.session_id)
        merged = ml_df.merge(rule_df, on="CitizenID", how="inner")
        merged["composite_score"] = merged["ml_risk_score"] + (0.5 * merged["rule_risk_score"])
        threshold = float(merged["composite_score"].quantile(0.80))
        merged["base_flag"] = ((merged["composite_score"] >= threshold) | (merged["rule_flag"] == 1)).astype(int)
        merged["final_flag"] = merged["base_flag"]

        llm_reviews = 0
        llm_overrides = 0
        if self.openrouter_client is not None and self.openrouter_client.enabled:
            # Review: (a) all flagged citizens, plus (b) borderline cases near threshold.
            # The +-0.15 window is too narrow for small datasets (<20 citizens);
            # scale the window relative to the score spread.
            score_range = merged["composite_score"].max() - merged["composite_score"].min()
            adaptive_band = max(0.30, score_range * 0.15)  # at least 0.30, or 15% of range
            borderline = (merged["composite_score"] - threshold).abs() <= adaptive_band
            review_mask = borderline | (merged["base_flag"] == 1)
            review_count = review_mask.sum()
            logger.info(
                "[DecisionAgent] LLM will review %d/%d citizens "
                "(adaptive_band=%.3f, threshold=%.4f)",
                review_count, len(merged), adaptive_band, threshold,
            )
            for idx in merged[review_mask].index:
                row = merged.loc[idx]
                payload = {
                    "CitizenID": row["CitizenID"],
                    "ml_risk_score": float(row["ml_risk_score"]),
                    "rule_risk_score": int(row["rule_risk_score"]),
                    "rule_flag": int(row["rule_flag"]),
                    "composite_score": float(row["composite_score"]),
                    "threshold": threshold,
                    "base_flag": int(row["base_flag"]),
                }
                llm_flag = self.openrouter_client.review_borderline_case(payload)
                if llm_flag is None:
                    continue
                llm_reviews += 1
                if llm_flag != int(row["base_flag"]):
                    llm_overrides += 1
                    logger.info(
                        "[DecisionAgent] LLM OVERRIDE CitizenID=%s: %d -> %d",
                        row["CitizenID"], int(row["base_flag"]), llm_flag,
                    )
                merged.at[idx, "final_flag"] = llm_flag
        elif self.openrouter_client is not None and not self.openrouter_client.enabled:
            logger.warning("[DecisionAgent] LLM client disabled — skipping all reviews")

        context.trace_client.event(
            name="decision_summary",
            output_payload={
                "session_id": context.session_id,
                "threshold": threshold,
                "final_flag_count": int(merged["final_flag"].sum()),
                "llm_reviews": llm_reviews,
                "llm_overrides": llm_overrides,
            },
        )
        return merged.sort_values("composite_score", ascending=False)
