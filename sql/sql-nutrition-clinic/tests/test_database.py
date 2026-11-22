"""Automated tests: python -m unittest discover tests"""
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import run  # noqa: E402


class TestClinic(unittest.TestCase):
    def setUp(self):
        self.conn = run.build_database(":memory:")

    def tearDown(self):
        self.conn.close()

    def test_every_query_returns_rows(self):
        for name, (_, sql) in run.load_queries().items():
            with self.subTest(query=name):
                self.assertGreater(len(self.conn.execute(sql).fetchall()), 0)

    def test_every_patient_has_one_latest_measurement(self):
        patients = self.conn.execute(
            "SELECT COUNT(DISTINCT patient_id) FROM appointments").fetchone()[0]
        latest = self.conn.execute("SELECT COUNT(*) FROM v_latest_measurement").fetchone()[0]
        self.assertEqual(patients, latest)

    def test_bmi_is_calculated_correctly(self):
        weight, height, bmi = self.conn.execute(
            "SELECT weight_kg, height_m, bmi FROM v_measurements_bmi LIMIT 1").fetchone()
        self.assertAlmostEqual(bmi, round(weight / height ** 2, 1))

    def test_trigger_rejects_visit_before_signup(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO appointments (patient_id, visit_date, visit_type, fee) "
                "VALUES (1, '1999-01-01', 'follow-up', 450)")

    def test_check_rejects_impossible_weight(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO measurements (appointment_id, weight_kg, height_m) VALUES (999999, 5, 1.70)")

    def test_foreign_keys_are_enforced(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO appointments (patient_id, visit_date, visit_type, fee) "
                "VALUES (9999, '2026-01-01', 'follow-up', 450)")


if __name__ == "__main__":
    unittest.main()
