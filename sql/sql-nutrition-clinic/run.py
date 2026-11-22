"""
Builds the project's SQLite database and runs the queries in sql/queries.sql.

Usage:
    python run.py              -> rebuild the database and run every query
    python run.py --list       -> list the available queries
    python run.py <name>       -> run a single query (e.g. python run.py current_bmi)
"""
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "clinic.db"
SCRIPTS = ["schema.sql", "seed.sql", "views.sql"]


def build_database(target=DB_PATH):
    """Create the database from scratch by running schema, seed data and views in order."""
    if target != ":memory:" and Path(target).exists():
        Path(target).unlink()
    conn = sqlite3.connect(target)
    conn.execute("PRAGMA foreign_keys = ON;")
    for name in SCRIPTS:
        conn.executescript((BASE / "sql" / name).read_text(encoding="utf-8"))
    conn.commit()
    return conn


def load_queries():
    """Read queries.sql and split it into blocks marked with '-- name: <name>'."""
    text = (BASE / "sql" / "queries.sql").read_text(encoding="utf-8")
    queries = {}
    current, description, lines = None, "", []
    for line in text.splitlines():
        if line.startswith("-- name:"):
            if current:
                queries[current] = (description, "\n".join(lines).strip())
            current, description, lines = line.split(":", 1)[1].strip(), "", []
        elif line.startswith("-- desc:") and current:
            description = line.split(":", 1)[1].strip()
        elif current:
            lines.append(line)
    if current:
        queries[current] = (description, "\n".join(lines).strip())
    return queries


def print_table(cursor, rows):
    columns = [c[0] for c in cursor.description]
    rows = [["" if v is None else str(v) for v in row] for row in rows]
    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c)
              for i, c in enumerate(columns)]
    print(" | ".join(c.ljust(w) for c, w in zip(columns, widths)))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(" | ".join(v.ljust(w) for v, w in zip(row, widths)))
    print(f"({len(rows)} rows)\n")


def main():
    # Avoid encoding errors with special characters in the Windows console
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    queries = load_queries()
    if "--list" in sys.argv:
        for name, (desc, _) in queries.items():
            print(f"{name:28} {desc}")
        return
    conn = build_database()
    print(f"Database created: {DB_PATH.name}\n")
    selected = [a for a in sys.argv[1:] if not a.startswith("--")] or list(queries)
    for name in selected:
        if name not in queries:
            print(f"Query '{name}' does not exist. Use --list to see them.")
            continue
        desc, sql = queries[name]
        print(f"=== {name} ===\n{desc}\n")
        cur = conn.execute(sql)
        print_table(cur, cur.fetchall())
    conn.close()


if __name__ == "__main__":
    main()
