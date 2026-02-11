# E-commerce Landing Page A/B Test Analysis (Production-Style Refactor)

## Executive summary
This repository upgrades a notebook-centric A/B test analysis into a reproducible analytics project with data validation, statistical decision support, business impact scenarios, SQL parity, and CI-ready quality controls.

## Tech stack
Python, pandas, numpy, scipy, statsmodels, seaborn/matplotlib, pytest, ruff, black, mypy.

## Quickstart
```bash
python -m pip install -e '.[dev]'
make run-analysis
```

Artifacts are generated in `outputs/` including metrics, figures, quality report, and decision report.

## Production workflow alignment
- Modular analysis code under `src/`
- Config-driven assumptions in `config/analysis.yaml`
- Automated script entrypoint (`scripts/run_analysis.py`)
- QA controls via tests and linting
- SQL file for BI/warehouse parity
- Documentation for experiment governance

## Key outputs
- `outputs/quality_report.json`
- `outputs/stats_results.json`
- `outputs/business_impact.csv`
- `outputs/report.md`
- `outputs/figures/*.png`
