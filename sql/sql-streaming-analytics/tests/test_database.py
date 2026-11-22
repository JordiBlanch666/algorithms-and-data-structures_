"""Automated tests: python -m unittest discover tests"""
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import run  # noqa: E402


class TestStreaming(unittest.TestCase):
    def setUp(self):
        self.conn = run.build_database(":memory:")

    def tearDown(self):
        self.conn.close()

    def test_every_query_returns_rows(self):
        for name, (_, sql) in run.load_queries().items():
            with self.subTest(query=name):
                self.assertGreater(len(self.conn.execute(sql).fetchall()), 0)

    def test_no_user_has_two_active_subscriptions(self):
        duplicates = self.conn.execute("""
            SELECT COUNT(*) FROM (SELECT user_id FROM subscriptions
                                  WHERE end_date IS NULL GROUP BY user_id HAVING COUNT(*) > 1)
        """).fetchone()[0]
        self.assertEqual(duplicates, 0)

    def test_partial_index_blocks_second_active_subscription(self):
        uid = self.conn.execute(
            "SELECT user_id FROM subscriptions WHERE end_date IS NULL LIMIT 1").fetchone()[0]
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO subscriptions (user_id, plan_id, start_date) VALUES (?, 1, '2026-10-01')",
                (uid,))

    def test_trigger_rejects_more_minutes_than_duration(self):
        tid, duration = self.conn.execute("SELECT id, duration_min FROM titles LIMIT 1").fetchone()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO plays (user_id, title_id, played_at, minutes_watched, device) "
                "VALUES (1, ?, '2026-10-01 20:00', ?, 'TV')", (tid, duration + 1))

    def test_cancellation_requires_reason(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO subscriptions (user_id, plan_id, start_date, end_date) "
                "VALUES (1, 1, '2024-01-01', '2024-02-01')")

    def test_recommendations_exclude_watched_titles(self):
        _, sql = run.load_queries()["recommendations"]
        recommended = {row[0] for row in self.conn.execute(sql)}
        watched = {row[0] for row in self.conn.execute(
            "SELECT DISTINCT title FROM v_plays WHERE user_id = 1")}
        self.assertFalse(recommended & watched)


if __name__ == "__main__":
    unittest.main()
