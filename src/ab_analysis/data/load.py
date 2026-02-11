from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_AB_COLUMNS = ["user_id", "timestamp", "group", "landing_page", "converted"]
REQUIRED_COUNTRY_COLUMNS = ["user_id", "country"]


def load_ab_data(path: str | Path) -> pd.DataFrame:
    """Load experiment assignment and outcome data."""
    return pd.read_csv(path)


def load_country_data(path: str | Path) -> pd.DataFrame:
    """Load country-level user metadata."""
    return pd.read_csv(path)
