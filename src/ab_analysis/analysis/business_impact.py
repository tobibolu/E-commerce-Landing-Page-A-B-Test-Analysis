from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Scenario:
    name: str
    monthly_visitors: int
    revenue_per_conversion: float
    rollout_percentage: float


def estimate_impact(absolute_lift: float, scenario: Scenario) -> dict[str, float | str]:
    """Estimate monthly and annual revenue impact for one rollout scenario."""
    effective_visitors = scenario.monthly_visitors * scenario.rollout_percentage
    monthly = effective_visitors * absolute_lift * scenario.revenue_per_conversion
    yearly = monthly * 12
    return {
        "scenario": scenario.name,
        "absolute_lift": absolute_lift,
        "monthly_revenue_impact": monthly,
        "yearly_revenue_impact": yearly,
    }
