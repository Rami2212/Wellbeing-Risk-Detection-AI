from __future__ import annotations

from pathlib import Path
import json
import pandas as pd


class DataLoader:
    def __init__(self, dataset_dir: Path) -> None:
        self.dataset_dir = dataset_dir

    def load_status(self) -> pd.DataFrame:
        status_path = self.dataset_dir / "status.csv"
        df = pd.read_csv(status_path)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        return df

    def load_users(self) -> pd.DataFrame:
        users_path = self.dataset_dir / "users.json"
        with users_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.json_normalize(data)

    def load_locations(self) -> pd.DataFrame:
        locations_path = self.dataset_dir / "locations.json"
        with locations_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.json_normalize(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return df

