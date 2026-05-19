"""
To-Do App CLI
=============
Author  : Jordi Yashua Contreras Blanch
GitHub  : github.com/JordiBlanch666
Contact : paastor.blanch@gmail.com
Course  : Software Engineering · Hybridge · 2nd semester

A command-line task manager with priorities, filters, and JSON persistence.
Every task survives between sessions — closing the terminal doesn't lose your data.

Concepts demonstrated:
  - CRUD operations (Create, Read, Update, Delete) on a JSON file
  - Filtering and sorting a list of dicts
  - Input validation with graceful error messages
  - State management without a database
  - Formatted table output with dynamic column widths
"""

import json
import os
from datetime import datetime

# ── Storage ───────────────────────────────────────────────────────────────────

FILE = os.path.join(os.path.dirname(__file__), "tasks.json")

PRIORITIES = {"high": 1, "medium": 2, "low": 3}   # lower number = shown first


# ── Persistence ───────────────────────────────────────────────────────────────

def load_tasks() -> list[dict]:
    """Load tasks from disk. Returns an empty list if the file doesn't exist yet."""
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks: list[dict]) -> None:
    """Write the current task list to disk as formatted JSON."""
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


# ── Task operations ───────────────────────────────────────────────────────────

def next_id(tasks: list[dict]) -> int:
    """Generate the next unique task ID — max existing ID + 1."""
    return max((t["id"] for t in tasks), default=0) + 1


def add_task(tasks: list[dict], title: str, priority: str = "medium") -> dict:
    """Create a new task and append it to the list."""
    priority = priority.lower()
    if priority not in PRIORITIES:
        raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}")

    task = {
        "id": next_id(tasks),
        "title": title.strip(),
        "priority": priority,
        "done": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def complete_task(tasks: list[dict], task_id: int) -> bool:
    """Mark a task as done. Returns False if the ID doesn't exist."""
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_tasks(tasks)
            return True
    return False


def delete_task(tasks: list[dict], task_id: int) -> bool:
    """Remove a task permanently. Returns False if the ID doesn't exist."""
    original_len = len(tasks)
    # List comprehension keeps every task EXCEPT the one with the given id.
    tasks[:] = [t for t in tasks if t["id"] != task_id]
    if len(tasks) < original_len:
        save_tasks(tasks)
        return True
    return False


def filter_tasks(tasks: list[dict], status: str = "all",
                 priority: str = "all") -> list[dict]:
    """
    Filter tasks by completion status and/or priority.
    Sorting by priority number puts 'high' tasks at the top.
    """
    result = tasks

    if status == "pending":
        result = [t for t in result if not t["done"]]
    elif status == "done":
        result = [t for t in result if t["done"]]

    if priority in PRIORITIES:
        result = [t for t in result if t["priority"] == priority]

    # Sort: pending first, then by priority level (high → medium → low)
    return sorted(result, key=lambda t: (t["done"], PRIORITIES.get(t["priority"], 99)))


# ── Display ───────────────────────────────────────────────────────────────────

PRIORITY_LABELS = {"high": "🔴 high", "medium": "🟡 med ", "low": "🟢 low "}
STATUS_ICONS = {True: "✓", False: "○"}


def print_tasks(tasks: list[dict]) -> None:
    if not tasks:
        print("  No tasks found.\n")
        return

    print(f"\n  {'ID':<4} {'St':<3} {'Pri':<8} {'Title':<35} Created")
    print("  " + "─" * 68)
    for t in tasks:
        icon = STATUS_ICONS[t["done"]]
        pri = PRIORITY_LABELS.get(t["priority"], t["priority"])
        title = t["title"][:34]   # truncate long titles for alignment
        print(f"  {t['id']:<4} {icon:<3} {pri:<8} {title:<35} {t['created_at']}")
    print()


def print_stats(tasks: list[dict]) -> None:
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    pending = total - done
    high = sum(1 for t in tasks if t["priority"] == "high" and not t["done"])
    print(f"  Total: {total}  |  Done: {done}  |  Pending: {pending}  |  High priority pending: {high}\n")


# ── Main loop ─────────────────────────────────────────────────────────────────

HELP_TEXT = """
  Commands:
    add <title>              add a task with medium priority
    add <title> -p high      add a task with high/medium/low priority
    done <id>                mark task as complete
    del <id>                 delete a task
    list                     show all tasks
    list pending             show only pending tasks
    list done                show only completed tasks
    list high                show only high-priority tasks
    stats                    show summary
    help                     show this menu
    exit                     quit
"""


def main() -> None:
    tasks = load_tasks()

    print("\n╔══════════════════════════════════════╗")
    print("║           To-Do App CLI              ║")
    print("║   Jordi Yashua Contreras Blanch      ║")
    print("╚══════════════════════════════════════╝")
    print(f"  {len(tasks)} task(s) loaded.  Type 'help' for commands.\n")

    while True:
        raw = input("  todo › ").strip()
        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        if cmd == "exit":
            print("\n  Goodbye!\n")
            break

        elif cmd == "help":
            print(HELP_TEXT)

        elif cmd == "stats":
            print_stats(tasks)

        elif cmd == "list":
            # Optional second argument: 'pending', 'done', 'high', 'medium', 'low'
            arg = parts[1].lower() if len(parts) > 1 else "all"
            if arg in ("pending", "done"):
                filtered = filter_tasks(tasks, status=arg)
            elif arg in PRIORITIES:
                filtered = filter_tasks(tasks, priority=arg)
            else:
                filtered = filter_tasks(tasks)
            print_tasks(filtered)

        elif cmd == "add":
            # Separate the title from the optional -p priority flag.
            # e.g. "add Buy groceries -p high" → title="Buy groceries", priority="high"
            if len(parts) < 2:
                print("  Usage: add <title> [-p high|medium|low]\n")
                continue
            priority = "medium"
            if "-p" in parts:
                p_idx = parts.index("-p")
                if p_idx + 1 < len(parts):
                    priority = parts[p_idx + 1]
                    title_parts = parts[1:p_idx]
                else:
                    print("  Missing priority value after -p.\n")
                    continue
            else:
                title_parts = parts[1:]
            title = " ".join(title_parts)
            try:
                task = add_task(tasks, title, priority)
                print(f"  ✓ Added [{task['id']}] '{task['title']}' ({task['priority']})\n")
            except ValueError as e:
                print(f"  Error: {e}\n")

        elif cmd == "done":
            try:
                task_id = int(parts[1])
                if complete_task(tasks, task_id):
                    print(f"  ✓ Task [{task_id}] marked as done.\n")
                else:
                    print(f"  Task [{task_id}] not found.\n")
            except (IndexError, ValueError):
                print("  Usage: done <id>\n")

        elif cmd == "del":
            try:
                task_id = int(parts[1])
                if delete_task(tasks, task_id):
                    print(f"  ✓ Task [{task_id}] deleted.\n")
                else:
                    print(f"  Task [{task_id}] not found.\n")
            except (IndexError, ValueError):
                print("  Usage: del <id>\n")

        else:
            print(f"  Unknown command '{cmd}'. Type 'help'.\n")


if __name__ == "__main__":
    main()
