"""
Exploratory data analysis (EDA): descriptive statistics and charts.
Charts are saved to the figures/ folder.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render images without opening windows
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.data import TARGET, bmi_class

FIGURES = Path(__file__).resolve().parent.parent / "figures"
COLOR = "#2E86AB"


def summary(df: pd.DataFrame) -> pd.DataFrame:
    """Rounded descriptive statistics."""
    return df.describe().T[["mean", "std", "min", "50%", "max"]].round(2)


def correlations_with_target(df: pd.DataFrame) -> pd.Series:
    """Pearson correlation of each variable with progression, sorted by strength."""
    corr = df.corr(numeric_only=True)[TARGET].drop(TARGET)
    return corr.reindex(corr.abs().sort_values(ascending=False).index).round(3)


def progression_by_bmi(df: pd.DataFrame) -> pd.DataFrame:
    """Average progression by BMI class (WHO)."""
    order = ["Underweight", "Normal", "Overweight", "Obesity"]
    table = (df.assign(bmi_class=df["bmi"].apply(bmi_class))
               .groupby("bmi_class")[TARGET]
               .agg(patients="count", avg_progression="mean")
               .round(1))
    return table.reindex([c for c in order if c in table.index])


def plot_distribution(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(df[TARGET], bins=30, color=COLOR, edgecolor="white")
    ax.axvline(df[TARGET].mean(), color="#E4572E", linestyle="--",
               label=f"Mean = {df[TARGET].mean():.0f}")
    ax.set(title="Distribution of diabetes progression after 1 year",
           xlabel="Progression (study scale)", ylabel="Patients")
    ax.legend()
    return _save(fig, "01_progression_distribution.png")


def plot_correlations(df: pd.DataFrame) -> Path:
    corr = correlations_with_target(df).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#E4572E" if v < 0 else COLOR for v in corr]
    ax.barh(corr.index, corr.values, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set(title="Correlation of each variable with progression",
           xlabel="Pearson coefficient")
    return _save(fig, "02_correlations.png")


def plot_bmi_vs_progression(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["bmi"], df[TARGET], alpha=0.55, color=COLOR, edgecolor="white")
    # Trend line (least squares)
    slope, intercept = np.polyfit(df["bmi"], df[TARGET], 1)
    x = np.sort(df["bmi"].to_numpy())
    ax.plot(x, slope * x + intercept, color="#E4572E", linewidth=2,
            label=f"+{slope:.1f} progression points per BMI point")
    for limit in (25, 30):
        ax.axvline(limit, color="gray", linestyle=":", linewidth=1)
    ax.set(title="BMI vs. diabetes progression", xlabel="BMI (kg/m²)", ylabel="Progression")
    ax.legend()
    return _save(fig, "03_bmi_vs_progression.png")


def _save(fig, name: str) -> Path:
    FIGURES.mkdir(exist_ok=True)
    path = FIGURES / name
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def run_eda(df: pd.DataFrame) -> None:
    print("=== Summary statistics ===")
    print(summary(df).to_string(), "\n")
    print("=== Correlation with progression ===")
    print(correlations_with_target(df).to_string(), "\n")
    print("=== Progression by BMI class (WHO) ===")
    print(progression_by_bmi(df).to_string(), "\n")
    for path in (plot_distribution(df), plot_correlations(df), plot_bmi_vs_progression(df)):
        print(f"Chart saved: figures/{path.name}")
    print()
