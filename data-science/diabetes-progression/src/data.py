"""
Loading and validating the diabetes dataset (Efron et al., 2004, bundled with scikit-learn).

442 diabetes patients. Baseline measurements plus a quantitative measure of disease
progression one year later (the target variable).
"""
import pandas as pd
from sklearn.datasets import load_diabetes

# Original column names -> descriptive names
COLUMNS = {
    "age": "age",
    "sex": "sex",
    "bmi": "bmi",
    "bp": "mean_blood_pressure",
    "s1": "total_cholesterol",
    "s2": "ldl",
    "s3": "hdl",
    "s4": "cholesterol_hdl_ratio",
    "s5": "log_triglycerides",
    "s6": "glucose",
    "target": "progression",
}

TARGET = "progression"


def load_data() -> pd.DataFrame:
    """Return the dataset with descriptive column names, in clinical units (unscaled)."""
    df = load_diabetes(as_frame=True, scaled=False).frame.rename(columns=COLUMNS)
    df["sex"] = df["sex"].astype(int)
    return df


def validate_data(df: pd.DataFrame) -> list[str]:
    """Check data quality. Returns a list of problems (empty list = all good)."""
    problems = []
    if df.isna().any().any():
        problems.append("Missing values found")
    if df.duplicated().any():
        problems.append("Duplicate rows found")
    if not df["bmi"].between(10, 70).all():
        problems.append("BMI outside physiological range")
    if not df["age"].between(0, 120).all():
        problems.append("Age out of range")
    if not df["hdl"].lt(df["total_cholesterol"]).all():
        problems.append("HDL greater than total cholesterol")
    return problems


def bmi_class(bmi: float) -> str:
    """WHO classification."""
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obesity"
