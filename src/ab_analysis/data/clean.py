from __future__ import annotations

import pandas as pd


def clean_experiment_data(ab_df: pd.DataFrame, countries_df: pd.DataFrame) -> pd.DataFrame:
    """Remove assignment mismatches and duplicated users; enrich with country data."""
    valid = ab_df[
        ((ab_df["group"] == "control") & (ab_df["landing_page"] == "old_page"))
        | ((ab_df["group"] == "treatment") & (ab_df["landing_page"] == "new_page"))
    ].copy()

    valid["timestamp"] = pd.to_datetime(valid["timestamp"], errors="coerce")
    valid = valid.sort_values("timestamp").drop_duplicates("user_id", keep="last")

    merged = valid.merge(countries_df, on="user_id", how="left")
    return merged
