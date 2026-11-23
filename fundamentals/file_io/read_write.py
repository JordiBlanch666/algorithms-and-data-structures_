"""
File Handling in Python
Shows how to read and write .txt and .csv files.
"""

import csv
import os

DIRECTORY = os.path.dirname(__file__)


# ── Text files ────────────────────────────────────────────────────────────────

def write_txt(path: str, lines: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(f"{line}\n" for line in lines)
    print(f"File '{path}' written ({len(lines)} lines).")


def read_txt(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


# ── CSV files ─────────────────────────────────────────────────────────────────

def write_csv(path: str, headers: list, rows: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV '{path}' written ({len(rows)} records).")


def read_csv(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # TXT
    courses = [
        "Algorithms and Design — Passed",
        "Git/GitHub Workshop  — Passed",
        "User Experience — In progress",
    ]
    txt_path = os.path.join(DIRECTORY, "courses.txt")
    write_txt(txt_path, courses)
    content = read_txt(txt_path)
    print("Read:", content)

    # CSV
    students = [
        {"name": "Ana García", "gpa": 9.5, "status": "Active"},
        {"name": "Carlos López", "gpa": 8.2, "status": "Active"},
        {"name": "María Martínez", "gpa": 7.8, "status": "Active"},
    ]
    csv_path = os.path.join(DIRECTORY, "students.csv")
    write_csv(csv_path, ["name", "gpa", "status"], students)

    records = read_csv(csv_path)
    print("\nCSV records:")
    for r in records:
        print(f"  {r['name']} → {r['gpa']}")
