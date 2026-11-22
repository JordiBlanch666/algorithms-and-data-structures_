"""Automated tests: python -m unittest discover tests"""
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import run  # noqa: E402


class TestHelpDesk(unittest.TestCase):
    def setUp(self):
        self.conn = run.build_database(":memory:")

    def tearDown(self):
        self.conn.close()

    def create_ticket(self):
        cur = self.conn.execute(
            "INSERT INTO tickets (user_id, agent_id, category_id, priority, title, created_at) "
            "VALUES (1, 1, 1, 'Medium', 'Test ticket', '2026-10-01 09:00:00')")
        return cur.lastrowid

    def test_every_query_returns_rows(self):
        for name, (_, sql) in run.load_queries().items():
            with self.subTest(query=name):
                self.assertGreater(len(self.conn.execute(sql).fetchall()), 0)

    def test_met_sla_is_consistent(self):
        # Compared against the exact (unrounded) time computed from the base table
        mismatches = self.conn.execute("""
            SELECT COUNT(*)
            FROM v_tickets_sla v
            JOIN tickets t ON t.id = v.id
            WHERE v.met_sla IS NOT NULL
              AND v.met_sla <> ((julianday(t.resolved_at) - julianday(t.created_at)) * 24
                                <= v.sla_resolution)""").fetchone()[0]
        self.assertEqual(mismatches, 0)

    def test_trigger_audits_status_change(self):
        tid = self.create_ticket()
        self.conn.execute("UPDATE tickets SET status = 'In progress' WHERE id = ?", (tid,))
        row = self.conn.execute(
            "SELECT old_status, new_status FROM status_history WHERE ticket_id = ?",
            (tid,)).fetchone()
        self.assertEqual(row, ("Open", "In progress"))

    def test_trigger_sets_resolution_date(self):
        tid = self.create_ticket()
        self.conn.execute("UPDATE tickets SET status = 'Resolved' WHERE id = ?", (tid,))
        resolved_at = self.conn.execute(
            "SELECT resolved_at FROM tickets WHERE id = ?", (tid,)).fetchone()[0]
        self.assertIsNotNone(resolved_at)

    def test_rejects_unknown_priority(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO tickets (user_id, category_id, priority, title, created_at) "
                "VALUES (1, 1, 'Super urgent', 'Test', '2026-10-01 09:00:00')")

    def test_rejects_invalid_email(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO users (full_name, email, department_id) VALUES ('X', 'no-at-sign', 1)")


if __name__ == "__main__":
    unittest.main()
