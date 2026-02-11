from __future__ import annotations

import pandas as pd


def conversion_metrics(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Aggregate conversion counts and rates."""
    metrics = (
        df.groupby(group_cols, dropna=False)
        .agg(
            users=("user_id", "nunique"),
            observations=("converted", "count"),
            conversions=("converted", "sum"),
            conversion_rate=("converted", "mean"),
        )
        .reset_index()
    )
    return metrics
