from __future__ import annotations

import numpy as np
import pandas as pd


def _slope(values: pd.Series) -> float:
    clean = values.dropna().astype(float)
    if len(clean) < 2:
        return 0.0
    x = np.arange(len(clean), dtype=float)
    y = clean.to_numpy(dtype=float)
    return float(np.polyfit(x, y, 1)[0])


def build_citizen_features(status_df: pd.DataFrame, locations_df: pd.DataFrame, users_df: pd.DataFrame) -> pd.DataFrame:
    status_sorted = status_df.sort_values(["CitizenID", "Timestamp"])

    grouped = status_sorted.groupby("CitizenID")
    feature_df = grouped.agg(
        event_count=("EventID", "count"),
        avg_activity=("PhysicalActivityIndex", "mean"),
        min_activity=("PhysicalActivityIndex", "min"),
        avg_sleep=("SleepQualityIndex", "mean"),
        min_sleep=("SleepQualityIndex", "min"),
        avg_exposure=("EnvironmentalExposureLevel", "mean"),
        max_exposure=("EnvironmentalExposureLevel", "max"),
        unique_event_types=("EventType", "nunique"),
    ).reset_index()

    trend_df = grouped.apply(
        lambda g: pd.Series(
            {
                "activity_slope": _slope(g["PhysicalActivityIndex"]),
                "sleep_slope": _slope(g["SleepQualityIndex"]),
                "exposure_slope": _slope(g["EnvironmentalExposureLevel"]),
            }
        ),
        include_groups=False,
    ).reset_index()

    loc_grouped = locations_df.groupby("user_id")
    loc_feature_df = loc_grouped.agg(
        location_points=("timestamp", "count"),
        lat_std=("lat", "std"),
        lng_std=("lng", "std"),
        cities_visited=("city", "nunique"),
    ).reset_index().rename(columns={"user_id": "CitizenID"})

    user_feature_df = users_df[["user_id", "birth_year"]].copy()
    user_feature_df["age_2026"] = 2026 - user_feature_df["birth_year"]
    user_feature_df = user_feature_df.rename(columns={"user_id": "CitizenID"})

    merged = feature_df.merge(trend_df, on="CitizenID", how="left")
    merged = merged.merge(loc_feature_df, on="CitizenID", how="left")
    merged = merged.merge(user_feature_df[["CitizenID", "age_2026"]], on="CitizenID", how="left")

    merged["lat_std"] = merged["lat_std"].fillna(0.0)
    merged["lng_std"] = merged["lng_std"].fillna(0.0)
    merged["cities_visited"] = merged["cities_visited"].fillna(1.0)

    return merged

