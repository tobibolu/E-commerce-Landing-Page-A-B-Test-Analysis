from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_conversion_by_group(df: pd.DataFrame, output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="group", y="converted", errorbar=("ci", 95))
    plt.title("Conversion Rate by Variant")
    plt.ylabel("Conversion rate")
    plt.xlabel("Variant")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()


def plot_conversion_by_country(df: pd.DataFrame, output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="country", y="converted", hue="group", errorbar=("ci", 95))
    plt.title("Conversion Rate by Country and Variant")
    plt.ylabel("Conversion rate")
    plt.xlabel("Country")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
