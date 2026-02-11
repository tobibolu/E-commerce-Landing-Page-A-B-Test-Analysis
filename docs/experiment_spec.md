# Experiment Spec

## Hypothesis
The new landing page (treatment) increases conversion rate relative to the old page (control).

## Primary metric
- Conversion rate (`converted`)

## Guardrails
- Sample Ratio Mismatch (SRM) assignment check
- Country-segment conversion consistency

## Statistical parameters
- Alpha: 0.05
- Power target: 0.80
- Minimum detectable effect (MDE): 0.5 percentage points

## Decision policy
- Roll out only if lift CI excludes 0 and practical impact is positive under base scenario.
