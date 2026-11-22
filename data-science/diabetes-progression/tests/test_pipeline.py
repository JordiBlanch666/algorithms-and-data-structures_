"""Automated tests: python -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import bmi_class, load_data, validate_data  # noqa: E402
from src.eda import correlations_with_target, progression_by_bmi  # noqa: E402
from src.models import BASELINE, compare_models, evaluate_on_test, split  # noqa: E402


class TestData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_data()

    def test_dataset_shape(self):
        self.assertEqual(self.df.shape, (442, 11))

    def test_data_is_valid(self):
        self.assertEqual(validate_data(self.df), [])

    def test_validation_catches_impossible_bmi(self):
        bad = self.df.copy()
        bad.loc[0, "bmi"] = 150
        self.assertIn("BMI outside physiological range", validate_data(bad))

    def test_bmi_class(self):
        self.assertEqual(bmi_class(17), "Underweight")
        self.assertEqual(bmi_class(24.9), "Normal")
        self.assertEqual(bmi_class(25), "Overweight")
        self.assertEqual(bmi_class(30), "Obesity")


class TestAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_data()

    def test_bmi_is_among_top_correlations(self):
        self.assertIn("bmi", correlations_with_target(self.df).index[:2])

    def test_obesity_progresses_more_than_normal(self):
        table = progression_by_bmi(self.df)
        self.assertGreater(table.loc["Obesity", "avg_progression"],
                           table.loc["Normal", "avg_progression"])


class TestModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_data()
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = split(cls.df)

    def test_split_has_no_overlap(self):
        self.assertEqual(len(set(self.X_train.index) & set(self.X_test.index)), 0)
        self.assertEqual(len(self.X_train) + len(self.X_test), len(self.df))

    def test_models_beat_baseline(self):
        table = compare_models(self.X_train, self.y_train).set_index("model")
        baseline = table.loc[BASELINE, "R2"]
        self.assertGreater(table.drop(BASELINE)["R2"].min(), baseline + 0.3)

    def test_best_model_generalizes(self):
        _, _, metrics = evaluate_on_test("Ridge", self.X_train, self.X_test, self.y_train, self.y_test)
        self.assertGreater(metrics["R2"], 0.35)


if __name__ == "__main__":
    unittest.main()
