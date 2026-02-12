# E-commerce Landing Page A/B Test Analysis

A rigorous statistical analysis of a landing page experiment involving 290K+ users, combining frequentist hypothesis testing, Bayesian inference, and power analysis to deliver actionable business recommendations.

## Key Results

| Metric | Value |
|--------|-------|
| Control conversion rate | 12.04% |
| Treatment conversion rate | 11.88% |
| Absolute difference | -0.16% |
| P-value (Z-test) | 0.1899 (not significant) |
| Cohen's h effect size | -0.005 (negligible) |
| P(treatment better) [Bayesian] | 9.4% |
| Estimated annual revenue impact | -$189K |
| **Recommendation** | **Keep current design** |

## What Makes This Project Different

- **Power analysis**: Calculates minimum detectable effect (MDE) and required sample sizes, answering "could this test even detect a meaningful difference?"
- **Bayesian analysis**: Complements frequentist testing with posterior distributions, probability of being better, and expected loss calculations
- **Multiple testing correction**: Bonferroni correction applied to country-level subgroup analysis
- **SQL analytics**: Full set of queries including daily funnels, cumulative conversions, and day-of-week patterns using CTEs and window functions
- **Interactive dashboard**: Streamlit app for stakeholders to explore results without running code

## Project Structure

```
├── app/
│   └── streamlit_app.py           # Interactive A/B test dashboard
├── data/
│   ├── ab_data.csv                # A/B test results (294,478 records)
│   └── countries.csv              # User country mapping (290,584 records)
├── notebooks/
│   └── abtest.ipynb               # Analysis notebook with full narrative
├── sql/
│   └── queries.sql                # Analytical SQL queries
├── src/
│   ├── data_loader.py             # Data loading and cleaning
│   ├── database.py                # SQLite integration and SQL analytics
│   ├── statistics.py              # Z-test, power analysis, Bayesian, Bonferroni
│   └── visualizations.py          # Plotting utilities
├── tests/
│   ├── test_data_loader.py        # Data validation tests
│   └── test_statistics.py         # Statistical function tests
├── requirements.txt
├── Makefile
└── .github/workflows/ci.yml
```

## Quick Start

```bash
pip install -r requirements.txt
make test
make run-app    # Launch interactive dashboard
```

## Statistical Methods

### 1. Frequentist Hypothesis Testing
Two-proportion Z-test with 95% confidence intervals. The test yields a p-value of 0.19, failing to reject the null hypothesis at alpha=0.05.

### 2. Power Analysis
With ~145K users per group and a baseline conversion of 12%, this test can reliably detect effects as small as ~0.3% absolute. The observed difference (-0.16%) falls below this threshold, meaning the test was underpowered for this effect size.

### 3. Bayesian A/B Testing
Using a Beta-Binomial conjugate model with uninformative Beta(1,1) priors:
- Posterior probability that treatment is better: 9.4%
- Expected loss if choosing treatment: 0.16 percentage points
- The Bayesian analysis reinforces the frequentist conclusion: the control is almost certainly better

### 4. Segmented Analysis with Multiple Testing Correction
Country-level analysis (US, UK, Canada) with Bonferroni correction adjusting alpha from 0.05 to 0.017. No segment shows a significant difference.

## SQL Analytics

Queries demonstrate:
- **Daily conversion funnels** with `DATE()` functions and `GROUP BY`
- **Running conversion rates** with cumulative window functions
- **Hourly patterns** with `LAG()` for period-over-period comparison
- **Day-of-week analysis** with `STRFTIME()` and `CASE`
- **Country performance** with traffic share using `SUM() OVER (PARTITION BY)`

See [`sql/queries.sql`](sql/queries.sql) for the full query set.

## Dataset

- **290,584** unique users after cleaning (from 294,478 raw records)
- **Test period**: January 2-24, 2017
- **Countries**: US (70%), UK (25%), Canada (5%)
- **Groups**: Near-perfect 50/50 split between control and treatment

## Tech Stack

Python 3.11 | pandas | NumPy | SciPy | statsmodels | Matplotlib | Seaborn | Streamlit | SQLite | pytest

## Live Demo

**[Launch Interactive Dashboard](https://ecommerce-landing-page-n4ktmi6daffgyxmbpmq3hh.streamlit.app/)**

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
