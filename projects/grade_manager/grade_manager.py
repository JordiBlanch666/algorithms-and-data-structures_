"""
Grade Manager
Demonstrates: functions, data structures, JSON files,
              loops, conditionals and error handling.
"""

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "grades.json")


# ── Persistence ───────────────────────────────────────────────────────────────

def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Business logic ────────────────────────────────────────────────────────────

def add_student(data: dict, name: str) -> None:
    name = name.strip().title()
    if name in data:
        print(f"  '{name}' already exists.")
        return
    data[name] = []
    save_data(data)
    print(f"  Student '{name}' added.")


def add_grade(data: dict, name: str, grade: float) -> None:
    name = name.strip().title()
    if name not in data:
        print(f"  Student '{name}' not found.")
        return
    if not (0 <= grade <= 100):
        print("  The grade must be between 0 and 100.")
        return
    data[name].append(grade)
    save_data(data)
    print(f"  Grade {grade} recorded for '{name}'.")


def calculate_average(grades: list) -> float:
    if not grades:
        return 0.0
    return sum(grades) / len(grades)


def letter_grade(average: float) -> str:
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    return "F"


def show_report(data: dict) -> None:
    if not data:
        print("  No students registered yet.")
        return

    print(f"\n  {'Student':<20} {'Grades':>6} {'Average':>9} {'Letter':>6}")
    print("  " + "-" * 45)

    for name, grades in sorted(data.items()):
        average = calculate_average(grades)
        letter = letter_grade(average) if grades else "-"
        total = len(grades)
        print(f"  {name:<20} {total:>6} {average:>9.1f} {letter:>6}")

    averages = [calculate_average(g) for g in data.values() if g]
    if averages:
        class_average = sum(averages) / len(averages)
        print(f"\n  Class average: {class_average:.1f}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def menu() -> None:
    data = load_data()

    options = {
        "1": "Add student",
        "2": "Record grade",
        "3": "View report",
        "4": "Exit",
    }

    print("\n╔══════════════════════════════╗")
    print("║        Grade Manager         ║")
    print("╚══════════════════════════════╝")

    while True:
        print()
        for key, description in options.items():
            print(f"  [{key}] {description}")

        option = input("\n  Choose an option: ").strip()

        if option == "1":
            name = input("  Student name: ")
            add_student(data, name)

        elif option == "2":
            name = input("  Student name: ")
            try:
                grade = float(input("  Grade (0-100): "))
                add_grade(data, name, grade)
            except ValueError:
                print("  Please enter a valid number.")

        elif option == "3":
            show_report(data)

        elif option == "4":
            print("\n  Goodbye!\n")
            break

        else:
            print("  Invalid option.")


if __name__ == "__main__":
    menu()
