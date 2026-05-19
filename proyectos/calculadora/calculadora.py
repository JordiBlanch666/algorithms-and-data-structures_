"""
Calculator CLI
==============
Author  : Jordi Yashua Contreras Blanch
GitHub  : github.com/JordiBlanch666
Contact : paastor.blanch@gmail.com
Course  : Software Engineering · Hybridge · 2nd semester

A command-line calculator that supports basic arithmetic, memory storage,
and a full history of operations — built with pure imperative programming.

Concepts demonstrated:
  - Functions with clear single responsibilities
  - Input validation and error handling (ZeroDivisionError, ValueError)
  - State management via a history list and memory variable
  - String parsing to split user expressions
  - Formatted output with f-strings
"""

import os


# ── Constants ─────────────────────────────────────────────────────────────────

OPERATORS = {"+", "-", "*", "/", "//", "%", "**"}

HELP_TEXT = """
  Commands:
    <num> <op> <num>   calculate   e.g. 12 * 5
    history            show all previous operations
    clear              clear the screen
    mc                 memory clear
    ms <num>           memory store   e.g. ms 42
    mr                 memory recall
    help               show this menu
    exit               quit
"""


# ── Core calculation ──────────────────────────────────────────────────────────

def calculate(a: float, operator: str, b: float) -> float:
    """
    Perform a single arithmetic operation.
    We use explicit if/elif instead of eval() for two reasons:
      1. eval() is a security risk — it can execute arbitrary Python code.
      2. Explicit branches make the code readable and easy to extend.
    """
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b
    elif operator == "//":
        # Integer (floor) division — useful for splitting things evenly.
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a // b
    elif operator == "%":
        # Modulo — remainder after division. Great for even/odd checks.
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a % b
    elif operator == "**":
        return a ** b
    else:
        raise ValueError(f"Unknown operator: '{operator}'")


def parse_expression(expression: str) -> tuple[float, str, float]:
    """
    Split a string like '12 * 5' into (12.0, '*', 5.0).
    We expect exactly three tokens separated by spaces.
    """
    parts = expression.strip().split()
    if len(parts) != 3:
        raise ValueError("Enter the expression as: <number> <operator> <number>")

    try:
        a = float(parts[0])
    except ValueError:
        raise ValueError(f"'{parts[0]}' is not a valid number.")

    operator = parts[1]
    if operator not in OPERATORS:
        raise ValueError(f"'{operator}' is not a supported operator. Use: {', '.join(sorted(OPERATORS))}")

    try:
        b = float(parts[2])
    except ValueError:
        raise ValueError(f"'{parts[2]}' is not a valid number.")

    return a, operator, b


def format_result(result: float) -> str:
    """
    Show integers without a decimal point, floats with up to 8 digits.
    12.0 → '12', 3.14159265 → '3.14159265'
    """
    if result == int(result):
        return str(int(result))
    return f"{result:.8g}"


# ── History ───────────────────────────────────────────────────────────────────

def print_history(history: list[str]) -> None:
    if not history:
        print("  No operations yet.")
        return
    print(f"\n  {'#':<4} {'Operation':<30} Result")
    print("  " + "-" * 50)
    for i, entry in enumerate(history, 1):
        print(f"  {i:<4} {entry}")
    print()


# ── Main loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    history: list[str] = []
    memory: float | None = None   # memory register — None means empty

    print("\n╔══════════════════════════════════════╗")
    print("║         Calculator CLI               ║")
    print("║   Jordi Yashua Contreras Blanch      ║")
    print("╚══════════════════════════════════════╝")
    print("  Type 'help' for commands.\n")

    while True:
        # Show memory indicator in the prompt if something is stored.
        mem_label = f" [M={format_result(memory)}]" if memory is not None else ""
        raw = input(f"  calc{mem_label} › ").strip().lower()

        if not raw:
            continue

        # ── Built-in commands ─────────────────────────────────────────────────
        if raw == "exit":
            print("\n  Goodbye!\n")
            break

        elif raw == "help":
            print(HELP_TEXT)

        elif raw == "history":
            print_history(history)

        elif raw == "clear":
            os.system("cls" if os.name == "nt" else "clear")

        elif raw == "mc":
            memory = None
            print("  Memory cleared.")

        elif raw == "mr":
            if memory is None:
                print("  Memory is empty.")
            else:
                print(f"  Memory: {format_result(memory)}")

        elif raw.startswith("ms "):
            # Memory store: "ms 42" or "ms 3.14"
            try:
                memory = float(raw[3:].strip())
                print(f"  Stored {format_result(memory)} in memory.")
            except ValueError:
                print("  Usage: ms <number>")

        # ── Arithmetic expression ─────────────────────────────────────────────
        else:
            try:
                a, operator, b = parse_expression(raw)
                result = calculate(a, operator, b)
                result_str = format_result(result)

                # Build a clean entry for the history log.
                a_str = format_result(a)
                b_str = format_result(b)
                entry = f"{a_str} {operator} {b_str} = {result_str}"
                history.append(entry)

                print(f"  = {result_str}")

            except (ValueError, ZeroDivisionError) as e:
                print(f"  Error: {e}")


if __name__ == "__main__":
    main()
