from __future__ import annotations

from pathlib import Path

from ab_analysis.analysis.stats_tests import ABResult


def write_markdown_report(
    output_path: str | Path,
    quality_report_path: str,
    ab_result: ABResult,
    recommendation: str,
) -> None:
    """Write a lightweight stakeholder-oriented report."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    content = f"""# A/B Test Decision Report

## Data Quality
- Quality report: `{quality_report_path}`

## Primary Experiment Outcome
- Control conversion rate: {ab_result.control_rate:.4%}
- Treatment conversion rate: {ab_result.treatment_rate:.4%}
- Absolute lift: {ab_result.absolute_lift:.4%}
- Relative lift: {ab_result.relative_lift:.2%}
- 95% CI for lift: [{ab_result.ci_low:.4%}, {ab_result.ci_high:.4%}]
- P-value: {ab_result.p_value:.4f}
- Cohen's h: {ab_result.cohens_h:.4f}

## Recommendation
{recommendation}
"""
    output.write_text(content)
