from pathlib import Path

import pandas as pd

from ab_analysis.analysis.business_impact import Scenario, estimate_impact
from ab_analysis.analysis.stats_tests import mde_sample_size, run_ab_test
from ab_analysis.data.clean import clean_experiment_data
from ab_analysis.data.validation import validate_experiment_data

FIXTURES = Path(__file__).parent / "fixtures"


def test_validation_and_cleaning_workflow() -> None:
    ab_df = pd.read_csv(FIXTURES / "ab_data_sample.csv")
    countries_df = pd.read_csv(FIXTURES / "countries_sample.csv")

    report = validate_experiment_data(ab_df, countries_df)
    assert report["row_count_ab"] == 5

    clean_df = clean_experiment_data(ab_df, countries_df)
    assert len(clean_df) == 2
    assert set(clean_df["group"]) == {"control", "treatment"}


def test_stats_and_business_impact() -> None:
    df = pd.DataFrame(
        {
            "user_id": [1, 2, 3, 4],
            "group": ["control", "control", "treatment", "treatment"],
            "converted": [0, 1, 1, 1],
        }
    )
    result = run_ab_test(df)
    assert result.treatment_rate >= result.control_rate

    scenario = Scenario("base", 1000, 50.0, 1.0)
    impact = estimate_impact(result.absolute_lift, scenario)
    assert "monthly_revenue_impact" in impact

    assert mde_sample_size(0.12, 0.01) > 0
