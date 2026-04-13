from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


@dataclass
class RiskModelArtifacts:
    scaler: StandardScaler
    model: IsolationForest
    feature_columns: List[str]


class RiskModel:
    def __init__(self, random_state: int, contamination: float) -> None:
        self.random_state = random_state
        self.contamination = contamination
        self.artifacts: Optional[RiskModelArtifacts] = None

    def fit(self, feature_df: pd.DataFrame) -> None:
        base_df = pd.DataFrame(feature_df)
        numeric_df = base_df.drop(columns=["CitizenID"], errors="ignore")
        numeric_df = pd.DataFrame(numeric_df).select_dtypes(include=["number"]).fillna(0.0)

        scaler = StandardScaler()
        scaled = scaler.fit_transform(numeric_df)

        model = IsolationForest(
            n_estimators=200,
            contamination=self.contamination,
            random_state=self.random_state,
        )
        model.fit(scaled)

        self.artifacts = RiskModelArtifacts(
            scaler=scaler,
            model=model,
            feature_columns=list(numeric_df.columns),
        )

    def score(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        if self.artifacts is None:
            raise RuntimeError("Model not fitted")

        numeric_df = feature_df[self.artifacts.feature_columns].fillna(0.0)
        scaled = self.artifacts.scaler.transform(numeric_df)

        # Lower decision function values indicate higher anomaly risk.
        anomaly_score = -self.artifacts.model.decision_function(scaled)
        preds = self.artifacts.model.predict(scaled)

        scored = pd.DataFrame({"CitizenID": feature_df["CitizenID"].to_numpy()})
        scored["ml_risk_score"] = anomaly_score
        scored["ml_flag"] = (preds == -1).astype(int)
        return scored

    def save(self, model_path: Path) -> None:
        if self.artifacts is None:
            raise RuntimeError("Model not fitted")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.artifacts, model_path)
