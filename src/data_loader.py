"""Data loading and cleaning for A/B test analysis."""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_ab_data(path: str = None) -> pd.DataFrame:
    """Load the A/B test dataset.

    Args:
        path: Path to CSV. Defaults to data/ab_data.csv.

    Returns:
        Raw A/B test DataFrame.
    """
    if path is None:
        path = os.path.join(DATA_DIR, "ab_data.csv")
    return pd.read_csv(path)


def load_countries(path: str = None) -> pd.DataFrame:
    """Load the country mapping dataset."""
    if path is None:
        path = os.path.join(DATA_DIR, "countries.csv")
    return pd.read_csv(path)


def clean_ab_data(df: pd.DataFrame, countries_df: pd.DataFrame) -> pd.DataFrame:
    """Clean A/B test data by removing mismatches and duplicates.

    Steps:
        1. Remove rows where group/landing_page are mismatched
        2. Convert timestamp to datetime
        3. Remove duplicate users (keep latest)
        4. Merge with country data

    Returns:
        Cleaned and enriched DataFrame.
    """
    # Remove mismatched landing pages
    df_clean = df.drop(df.query(
        '(group == "treatment" and landing_page != "new_page") or '
        '(group != "treatment" and landing_page == "new_page") or '
        '(group == "control" and landing_page != "old_page") or '
        '(group != "control" and landing_page == "old_page")'
    ).index)

    # Parse timestamps and deduplicate
    df_clean = df_clean.copy()
    df_clean["timestamp"] = pd.to_datetime(df_clean["timestamp"])
    df_clean = df_clean.sort_values("timestamp").drop_duplicates("user_id", keep="last")

    # Merge country data
    df_final = df_clean.merge(countries_df, on="user_id", how="left")

    return df_final


def get_cleaning_summary(original_len: int, clean_len: int) -> dict:
    """Return a summary of the cleaning process."""
    return {
        "original_records": original_len,
        "clean_records": clean_len,
        "removed_records": original_len - clean_len,
        "pct_removed": round((original_len - clean_len) / original_len * 100, 2),
    }
