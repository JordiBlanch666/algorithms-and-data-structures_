"""
Models that predict diabetes progression.

Workflow:
1. Split 80% training / 20% test (fixed seed).
2. Compare 4 models with 5-fold cross-validation on the training set.
3. Evaluate the best model once on the test set.
4. Explain the model with permutation importance.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.data import TARGET

SEED = 42
ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
BASELINE = "Baseline (mean)"


def build_models() -> dict:
    """Models to compare. Linear models are scaled inside a pipeline (no data leakage)."""
    return {
        BASELINE: DummyRegressor(strategy="mean"),
        "Linear regression": make_pipeline(StandardScaler(), LinearRegression()),
        "Ridge": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "Random Forest": RandomForestRegressor(n_estimators=300, min_samples_leaf=5,
                                               random_state=SEED, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=150, max_depth=2,
                                                       learning_rate=0.05, random_state=SEED),
    }


def split(df: pd.DataFrame):
    X, y = df.drop(columns=TARGET), df[TARGET]
    return train_test_split(X, y, test_size=0.2, random_state=SEED)


def compare_models(X_train, y_train) -> pd.DataFrame:
    """5-fold cross-validation. Returns the average metrics for each model."""
    cv = KFold(n_splits=5, shuffle=True, random_state=SEED)
    rows = []
    for name, model in build_models().items():
        r = cross_validate(model, X_train, y_train, cv=cv,
                           scoring=("r2", "neg_mean_absolute_error", "neg_root_mean_squared_error"))
        rows.append({
            "model": name,
            "R2": r["test_r2"].mean(),
            "R2_std": r["test_r2"].std(),
            "MAE": -r["test_neg_mean_absolute_error"].mean(),
            "RMSE": -r["test_neg_root_mean_squared_error"].mean(),
        })
    return pd.DataFrame(rows).sort_values("R2", ascending=False).round(3).reset_index(drop=True)


def evaluate_on_test(name: str, X_train, X_test, y_train, y_test):
    model = build_models()[name].fit(X_train, y_train)
    pred = model.predict(X_test)
    metrics = {
        "model": name,
        "R2": round(r2_score(y_test, pred), 3),
        "MAE": round(mean_absolute_error(y_test, pred), 1),
        "RMSE": round(root_mean_squared_error(y_test, pred), 1),
    }
    return model, pred, metrics


def feature_importance(model, X_test, y_test) -> pd.Series:
    """How much R² drops when each variable is shuffled (model-agnostic method)."""
    r = permutation_importance(model, X_test, y_test, n_repeats=30,
                               random_state=SEED, scoring="r2")
    return pd.Series(r.importances_mean, index=X_test.columns).sort_values(ascending=False).round(3)


def plot_comparison(table: pd.DataFrame) -> Path:
    t = table.sort_values("R2")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(t["model"], t["R2"], xerr=t["R2_std"], color="#2E86AB", capsize=4)
    ax.set(title="Model comparison (5-fold cross-validation)",
           xlabel="Mean R² (higher is better)")
    return _save(fig, "04_model_comparison.png")


def plot_actual_vs_predicted(y_test, pred, name: str) -> Path:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_test, pred, alpha=0.7, color="#2E86AB", edgecolor="white")
    limits = [min(y_test.min(), pred.min()), max(y_test.max(), pred.max())]
    ax.plot(limits, limits, "--", color="#E4572E", label="Perfect prediction")
    ax.set(title=f"Actual vs. predicted — {name}", xlabel="Actual progression",
           ylabel="Predicted progression")
    ax.legend()
    return _save(fig, "05_actual_vs_predicted.png")


def plot_importance(imp: pd.Series) -> Path:
    imp = imp.sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(imp.index, imp.values, color="#2E86AB")
    ax.set(title="Feature importance (permutation)", xlabel="Drop in R² when the variable is shuffled")
    return _save(fig, "06_feature_importance.png")


def _save(fig, name: str) -> Path:
    FIGURES.mkdir(exist_ok=True)
    path = FIGURES / name
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def run_models(df: pd.DataFrame) -> dict:
    np.random.seed(SEED)
    X_train, X_test, y_train, y_test = split(df)
    print(f"Training: {len(X_train)} patients | Test: {len(X_test)} patients\n")

    table = compare_models(X_train, y_train)
    print("=== Cross-validation (5 folds) ===")
    print(table.to_string(index=False), "\n")

    best = table.iloc[0]["model"]
    model, pred, metrics = evaluate_on_test(best, X_train, X_test, y_train, y_test)
    print(f"=== Best model on the test set: {best} ===")
    print(metrics, "\n")

    imp = feature_importance(model, X_test, y_test)
    print("=== Feature importance ===")
    print(imp.to_string(), "\n")

    RESULTS.mkdir(exist_ok=True)
    table.to_csv(RESULTS / "model_comparison.csv", index=False)
    pd.DataFrame([metrics]).to_csv(RESULTS / "test_metrics.csv", index=False)
    imp.rename("importance").to_csv(RESULTS / "feature_importance.csv")

    for path in (plot_comparison(table), plot_actual_vs_predicted(y_test, pred, best),
                 plot_importance(imp)):
        print(f"Chart saved: figures/{path.name}")
    return {"table": table, "metrics": metrics, "importance": imp}
