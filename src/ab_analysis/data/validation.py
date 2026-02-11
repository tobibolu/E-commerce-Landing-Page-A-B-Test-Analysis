from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd

from ab_analysis.data.load import REQUIRED_AB_COLUMNS, REQUIRED_COUNTRY_COLUMNS


class DataValidationError(ValueError):
    """Raised when dataset contract checks fail."""


def _missing_columns(df: pd.DataFrame, required: Iterable[str]) -> list[str]:
    return [col for col in required if col not in df.columns]


def validate_experiment_data(ab_df: pd.DataFrame, countries_df: pd.DataFrame) -> dict[str, Any]:
    """Validate schema and constraints for experiment inputs."""
    errors: list[str] = []

    missing_ab = _missing_columns(ab_df, REQUIRED_AB_COLUMNS)
    if missing_ab:
        errors.append(f"ab_data missing columns: {missing_ab}")

    missing_country = _missing_columns(countries_df, REQUIRED_COUNTRY_COLUMNS)
    if missing_country:
        errors.append(f"countries_data missing columns: {missing_country}")

    if "group" in ab_df.columns:
        invalid_group = sorted(set(ab_df[~ab_df["group"].isin(["control", "treatment"])]["group"]))
        if invalid_group:
            errors.append(f"invalid group values: {invalid_group}")

    if "landing_page" in ab_df.columns:
        invalid_page = sorted(
            set(ab_df[~ab_df["landing_page"].isin(["old_page", "new_page"])]["landing_page"])
        )
        if invalid_page:
            errors.append(f"invalid landing_page values: {invalid_page}")

    if "converted" in ab_df.columns:
        invalid_conv = sorted(set(ab_df[~ab_df["converted"].isin([0, 1])]["converted"]))
        if invalid_conv:
            errors.append(f"invalid converted values: {invalid_conv}")

    duplicates_by_user = int(ab_df["user_id"].duplicated().sum()) if "user_id" in ab_df.columns else 0
    mismatches = int(
        (
            ((ab_df["group"] == "control") & (ab_df["landing_page"] != "old_page"))
            | ((ab_df["group"] == "treatment") & (ab_df["landing_page"] != "new_page"))
        ).sum()
    )

    ab_users = set(ab_df["user_id"].astype(str))
    country_users = set(countries_df["user_id"].astype(str))
    users_missing_country = len(ab_users - country_users)
    country_without_ab = len(country_users - ab_users)

    report = {
        "row_count_ab": int(len(ab_df)),
        "row_count_countries": int(len(countries_df)),
        "duplicate_users_ab": duplicates_by_user,
        "mismatch_rows": mismatches,
        "users_missing_country": users_missing_country,
        "country_users_missing_ab": country_without_ab,
        "errors": errors,
    }

    if errors:
        raise DataValidationError("; ".join(errors))

    return report


def write_quality_report(report: dict[str, Any], output_path: str | Path) -> None:
    """Persist validation summary for pipeline observability."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
