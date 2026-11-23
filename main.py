"""
Portfolio — Jordi Yashua Contreras Blanch
Software Engineering · Hybridge

Runs demos from each portfolio module.
"""

import sys

# Windows terminals default to cp1252 which can't render box-drawing characters.
# This forces UTF-8 output so the portfolio menu displays correctly.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _ask_for_list() -> list:
    raw = input("\n  Enter your list separated by commas (e.g. 45, 12, 78, 3, 56): ").strip()
    try:
        return [int(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError:
        print("  Invalid list — integers separated by commas only.")
        return []


def _bubble_steps(lst: list, verbose: bool) -> tuple:
    arr = lst.copy()
    n, comparisons, swaps, passes = len(arr), 0, 0, 0
    for i in range(n - 1):
        swapped = False
        passes += 1
        for j in range(n - 1 - i):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if verbose:
            print(f"    Pass {passes}: {arr}  (swapped: {'yes' if swapped else 'no'})")
        if not swapped:
            break
    return arr, comparisons, swaps, passes


def _insertion_steps(lst: list, verbose: bool) -> tuple:
    arr = lst.copy()
    comparisons, moves = 0, 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            comparisons += 1
            arr[j + 1] = arr[j]
            moves += 1
            j -= 1
        arr[j + 1] = key
        if verbose:
            print(f"    Insert {key:>4}: {arr}")
    return arr, comparisons, moves


def _selection_steps(lst: list, verbose: bool) -> tuple:
    arr = lst.copy()
    n, comparisons, swaps = len(arr), 0, 0
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        if min_idx != i:
            swaps += 1
        if verbose:
            print(f"    Minimum → pos {i}: {arr}")
    return arr, comparisons, swaps


def _demo_sorting(data: list):
    verbose = input("\n  Show step by step? [y/n]: ").strip().lower() == "y"
    print(f"\n  Original list: {data}\n")

    print("  ── Bubble Sort ──")
    res, comp, swaps, passes = _bubble_steps(data, verbose)
    print(f"  Result:      {res}")
    print(f"  Passes: {passes}  |  Comparisons: {comp}  |  Swaps: {swaps}\n")

    print("  ── Insertion Sort ──")
    res, comp, movs = _insertion_steps(data, verbose)
    print(f"  Result:  {res}")
    print(f"  Comparisons: {comp}  |  Moves: {movs}\n")

    print("  ── Selection Sort ──")
    res, comp, swaps = _selection_steps(data, verbose)
    print(f"  Result:  {res}")
    print(f"  Comparisons: {comp}  |  Swaps: {swaps}")


def _demo_search(data: list):
    from algorithms.searching.linear_search import linear_search
    from algorithms.searching.binary_search import binary_search

    try:
        target = int(input("\n  Which number are you looking for? ").strip())
    except ValueError:
        print("  Invalid number.")
        return

    verbose = input("  Show step by step? [y/n]: ").strip().lower() == "y"
    print()

    # Linear search
    linear_steps = 0
    linear_idx = -1
    for i, val in enumerate(data):
        linear_steps += 1
        if verbose:
            marker = " ← FOUND" if val == target else ""
            print(f"    Linear  [{i}] = {val}{marker}")
        if val == target:
            linear_idx = i
            break

    if linear_idx == -1 and verbose:
        print(f"    Linear  — {target} is not in the list")

    linear_result = f"index {linear_idx}" if linear_idx != -1 else "not found"
    print(f"\n  Linear:  {linear_result}  ({linear_steps} comparisons)")

    # Binary search (requires a sorted list)
    sorted_data = sorted(data)
    left, right, binary_steps, binary_idx = 0, len(sorted_data) - 1, 0, -1
    while left <= right:
        mid = (left + right) // 2
        binary_steps += 1
        if verbose:
            print(f"    Binary  [{left}..{right}] mid={mid} → {sorted_data[mid]}", end="")
        if sorted_data[mid] == target:
            binary_idx = mid
            if verbose:
                print(" ← FOUND")
            break
        elif sorted_data[mid] < target:
            if verbose:
                print(" → search right")
            left = mid + 1
        else:
            if verbose:
                print(" → search left")
            right = mid - 1

    binary_result = f"index {binary_idx} in sorted list {sorted_data}" if binary_idx != -1 else "not found"
    print(f"  Binary:  {binary_result}  ({binary_steps} comparisons)")


def _demo_fibonacci():
    try:
        n = int(input("\n  Fibonacci(n) — enter n: ").strip())
    except ValueError:
        print("  Invalid number.")
        return

    verbose = input("  Show each computed F(i)? [y/n]: ").strip().lower() == "y"

    memo = {0: 0, 1: 1}

    def fib(k):
        if k in memo:
            return memo[k]
        memo[k] = fib(k - 1) + fib(k - 2)
        if verbose:
            print(f"    F({k}) = F({k-1}) + F({k-2}) = {memo[k-1]} + {memo[k-2]} = {memo[k]}")
        return memo[k]

    if verbose:
        print(f"    F(0) = 0  (base)")
        print(f"    F(1) = 1  (base)")
    sequence = [fib(i) for i in range(n + 1)]
    print(f"\n  F(0) to F({n}): {sequence}")
    print(f"  F({n}) = {sequence[-1]}")


def demo_algorithms():
    data = _ask_for_list()
    if not data:
        return

    while True:
        print(f"\n  Your list: {data}")
        print("  [1] Sort — Bubble, Insertion, Selection")
        print("  [2] Search for a value")
        print("  [3] Fibonacci(n)")
        print("  [0] Back")

        choice = input("\n  Option: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            _demo_sorting(data)
        elif choice == "2":
            _demo_search(data)
        elif choice == "3":
            _demo_fibonacci()
        else:
            print("  Invalid option.")


def demo_data_structures():
    from data_structures.stack import Stack, check_brackets
    from data_structures.fifo_queue import Queue

    stack = Stack()
    for v in [10, 20, 30]:
        stack.push(v)
    print(f"  Stack: {stack}  → pop: {stack.pop()}")

    queue = Queue()
    for v in ["A", "B", "C"]:
        queue.enqueue(v)
    print(f"  Queue: {queue}  → dequeue: {queue.dequeue()}")

    expressions = ["(a + b) * [c]", "((x + y)", "{a + [b]}"]
    print("\n  Bracket validation:")
    for expr in expressions:
        status = "✓" if check_brackets(expr) else "✗"
        print(f"    {status}  {expr}")


def demo_oop():
    from oop.banking_system import SavingsAccount, CheckingAccount

    print("  — Savings Account —")
    savings = SavingsAccount("Jordi Blanch", 1000.0, interest_rate=0.05)
    savings.deposit(500)
    savings.apply_interest()
    print(savings)

    print("\n  — Checking Account —")
    checking = CheckingAccount("Ana García", 200.0, overdraft_limit=300.0)
    checking.withdraw(400)
    print(checking)


MODULES = {
    "1": ("Algorithms (sorting, searching, recursion)", demo_algorithms),
    "2": ("Data structures (Stack, Queue)",             demo_data_structures),
    "3": ("OOP — Banking System",                       demo_oop),
}


def main():
    print("\n╔══════════════════════════════════════════╗")
    print("║   Portfolio · Jordi Contreras Blanch    ║")
    print("║   Software Engineering · Hybridge       ║")
    print("╚══════════════════════════════════════════╝\n")

    for key, (name, _) in MODULES.items():
        print(f"  [{key}] {name}")
    print("  [0] Exit\n")

    choice = input("  Choose a module: ").strip()

    if choice == "0":
        sys.exit(0)

    if choice not in MODULES:
        print("  Invalid option.")
        return

    name, fn = MODULES[choice]
    print(f"\n── {name} ──────────────────────────────────\n")
    fn()
    print()


if __name__ == "__main__":
    main()
