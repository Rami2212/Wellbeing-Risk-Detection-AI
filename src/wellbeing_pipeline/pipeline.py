from __future__ import annotations

from pathlib import Path
import pandas as pd

from .agents import AgentContext, DataIngestionAgent, FeatureAgent, MLRiskAgent, RuleRiskAgent, DecisionAgent
from .config import PipelineConfig, load_langfuse_config, load_openrouter_config
from .data_loader import DataLoader
from .langfuse_utils import build_trace_client
from .openrouter_client import OpenRouterDecisionClient


def write_output_ascii(results_df: pd.DataFrame, output_path: Path) -> list[str]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    flagged_series = results_df["CitizenID"].where(results_df["final_flag"] == 1)
    flagged_ids = flagged_series.dropna().astype(str).to_list()

    with output_path.open("w", encoding="ascii", errors="ignore") as f:
        for citizen_id in flagged_ids:
            f.write(f"{citizen_id}\n")

    return flagged_ids


def run_pipeline(config: PipelineConfig) -> tuple[pd.DataFrame, list[str]]:
    trace_client = build_trace_client(load_langfuse_config())
    trace_client.start_run(config.session_id)
    context = AgentContext(session_id=config.session_id, trace_client=trace_client)

    loader = DataLoader(dataset_dir=config.dataset_dir)
    ingestion_agent = DataIngestionAgent()
    feature_agent = FeatureAgent()
    ml_agent = MLRiskAgent(random_state=config.random_state, contamination=config.contamination)
    rule_agent = RuleRiskAgent()
    openrouter_client = OpenRouterDecisionClient(load_openrouter_config())
    decision_agent = DecisionAgent(openrouter_client=openrouter_client)

    data = ingestion_agent.run(loader, context)
    features = feature_agent.run(data, context)
    ml_scores = ml_agent.run(features, context)
    rule_scores = rule_agent.run(features, context)
    decisions = decision_agent.run(ml_scores, rule_scores, context)

    ml_agent.model.save(config.model_path)
    flagged_ids = write_output_ascii(decisions, config.output_file)
    trace_client.flush()

    return decisions, flagged_ids

