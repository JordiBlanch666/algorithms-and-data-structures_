"""
Diabetes progression prediction — full pipeline.

    python main.py
"""
import sys

from src.data import load_data, validate_data
from src.eda import run_eda
from src.models import run_models


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # special characters in the Windows console

    df = load_data()
    print(f"Dataset: {df.shape[0]} patients, {df.shape[1] - 1} features\n")

    problems = validate_data(df)
    print("Data validation:", "OK" if not problems else problems, "\n")

    run_eda(df)
    run_models(df)


if __name__ == "__main__":
    main()
