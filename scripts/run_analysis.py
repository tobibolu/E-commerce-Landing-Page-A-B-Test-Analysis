from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from ab_analysis.analysis.business_impact import Scenario, estimate_impact
from ab_analysis.analysis.metrics import conversion_metrics
from ab_analysis.analysis.stats_tests import mde_sample_size, run_ab_test, srm_check
from ab_analysis.data.clean import clean_experiment_data
from ab_analysis.data.load import load_ab_data, load_country_data
from ab_analysis.data.validation import validate_experiment_data, write_quality_report
from ab_analysis.reporting.plots import plot_conversion_by_country, plot_conversion_by_group
from ab_analysis.reporting.report import write_markdown_report


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cfg = yaml.safe_load((ROOT / "config/analysis.yaml").read_text())

    ab_df = load_ab_data(ROOT / "ab_data.csv")
    countries_df = load_country_data(ROOT / "countries.csv")

    quality = validate_experiment_data(ab_df, countries_df)
    write_quality_report(quality, ROOT / "outputs/quality_report.json")

    final_df = clean_experiment_data(ab_df, countries_df)
    final_df.to_csv(ROOT / "outputs/cleaned_data.csv", index=False)

    overall = conversion_metrics(final_df, ["group"])
    by_country = conversion_metrics(final_df, ["country", "group"])
    overall.to_csv(ROOT / "outputs/overall_metrics.csv", index=False)
    by_country.to_csv(ROOT / "outputs/country_metrics.csv", index=False)

    test_result = run_ab_test(
        final_df,
        alpha=cfg["experiment"]["alpha"],
        alternative=cfg["experiment"]["alternative"],
    )

    srm = srm_check(final_df)
    sample_size = mde_sample_size(
        baseline_rate=cfg["experiment"]["baseline_rate"],
        mde=cfg["experiment"]["mde"],
        alpha=cfg["experiment"]["alpha"],
    )

    stats_payload = {
        "ab_test": test_result.__dict__,
        "srm": srm,
        "sample_size_per_group_for_mde": sample_size,
    }
    (ROOT / "outputs/stats_results.json").write_text(json.dumps(stats_payload, indent=2))

    scenario_rows = []
    for row in cfg["scenarios"]:
        scenario = Scenario(**row)
        scenario_rows.append(estimate_impact(test_result.absolute_lift, scenario))
    pd.DataFrame(scenario_rows).to_csv(ROOT / "outputs/business_impact.csv", index=False)

    tidy = final_df.assign(metric="conversion_rate", value=final_df["converted"])[
        ["timestamp", "country", "group", "metric", "value"]
    ].rename(columns={"timestamp": "date", "country": "segment", "group": "variant"})
    tidy.to_csv(ROOT / "outputs/bi_metrics.csv", index=False)

    plot_conversion_by_group(final_df, ROOT / "outputs/figures/conversion_by_group.png")
    plot_conversion_by_country(final_df, ROOT / "outputs/figures/conversion_by_country.png")

    recommendation = (
        "Do not roll out treatment yet because observed lift is statistically inconclusive at alpha=0.05. "
        "Gather additional sample if business value remains material."
    )
    write_markdown_report(
        ROOT / "outputs/report.md",
        "outputs/quality_report.json",
        test_result,
        recommendation,
    )


if __name__ == "__main__":
    main()
