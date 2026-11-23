"""
Quiz App CLI
============
Author  : Jordi Yashua Contreras Blanch
GitHub  : github.com/JordiBlanch666
Contact : paastor.blanch@gmail.com
Course  : Software Engineering · Hybridge · 2nd semester

A multiple-choice quiz with two categories: Python fundamentals and
Networking basics — both relevant to the 2nd semester curriculum.

Concepts demonstrated:
  - Lists of dicts as a simple in-memory data structure
  - Randomizing question order with random.sample()
  - Score tracking and percentage calculation
  - Timed questions using the time module
  - Conditional feedback per answer
"""

import random
import time
import os

# ── Question bank ─────────────────────────────────────────────────────────────
# Each question is a dict with:
#   question  : the prompt
#   options   : list of 4 choices (always 4)
#   answer    : index of the correct option (0-based)
#   explanation: shown after answering — "why" not just "what"

QUESTIONS = {
    "python": [
        {
            "question": "What is the time complexity of accessing an element in a Python list by index?",
            "options": ["O(n)", "O(log n)", "O(1)", "O(n²)"],
            "answer": 2,
            "explanation": "Lists store elements in contiguous memory, so index access is always O(1).",
        },
        {
            "question": "Which data structure uses LIFO order?",
            "options": ["Queue", "Stack", "Linked list", "Heap"],
            "answer": 1,
            "explanation": "Stack = Last In, First Out. Think of a stack of plates.",
        },
        {
            "question": "What does 'self' refer to in a Python class method?",
            "options": [
                "The class itself",
                "The current instance of the class",
                "The parent class",
                "A global variable",
            ],
            "answer": 1,
            "explanation": "'self' is a reference to the specific object that called the method.",
        },
        {
            "question": "What keyword makes a method unavailable for direct instantiation in Python's ABC?",
            "options": ["@staticmethod", "@classmethod", "@abstractmethod", "@property"],
            "answer": 2,
            "explanation": "@abstractmethod forces subclasses to implement the method; the base class can't be instantiated.",
        },
        {
            "question": "What is the best-case time complexity of Bubble Sort?",
            "options": ["O(n²)", "O(n log n)", "O(n)", "O(1)"],
            "answer": 2,
            "explanation": "With the early-exit (swapped flag), if the list is already sorted, only one pass is needed — O(n).",
        },
        {
            "question": "Which collection type in Python has O(1) average-time membership testing?",
            "options": ["list", "tuple", "set", "deque"],
            "answer": 2,
            "explanation": "Sets use hash tables internally, making 'x in s' O(1) on average.",
        },
        {
            "question": "What does @property allow you to do in Python?",
            "options": [
                "Define a class-level constant",
                "Access a method as if it were an attribute",
                "Create a private method",
                "Override the constructor",
            ],
            "answer": 1,
            "explanation": "@property lets you write obj.balance instead of obj.get_balance(), while still running validation logic.",
        },
        {
            "question": "In Binary Search, what MUST be true about the input list?",
            "options": ["It must contain unique elements", "It must be sorted", "It must have an even length", "It must be a list of integers"],
            "answer": 1,
            "explanation": "Binary Search halves the search space by comparing to the middle element — this only works if the list is sorted.",
        },
    ],
    "networking": [
        {
            "question": "What does DNS stand for?",
            "options": [
                "Data Network System",
                "Domain Name System",
                "Digital Node Service",
                "Direct Network Socket",
            ],
            "answer": 1,
            "explanation": "DNS translates human-readable hostnames (google.com) into IP addresses (142.250.80.46).",
        },
        {
            "question": "Which HTTP status code means 'Not Found'?",
            "options": ["200", "301", "403", "404"],
            "answer": 3,
            "explanation": "404 means the server couldn't find the requested resource. 200=OK, 301=Redirect, 403=Forbidden.",
        },
        {
            "question": "What protocol guarantees delivery and order of packets?",
            "options": ["UDP", "IP", "TCP", "HTTP"],
            "answer": 2,
            "explanation": "TCP (Transmission Control Protocol) ensures data arrives in order and without errors. UDP sacrifices that for speed.",
        },
        {
            "question": "What is the default port for HTTPS?",
            "options": ["80", "443", "8080", "22"],
            "answer": 1,
            "explanation": "HTTPS runs on port 443 by default. HTTP uses 80, SSH uses 22, and 8080 is a common alternative for HTTP.",
        },
        {
            "question": "What IP address always refers to your own machine?",
            "options": ["192.168.0.1", "255.255.255.0", "127.0.0.1", "0.0.0.0"],
            "answer": 2,
            "explanation": "127.0.0.1 is the loopback address — traffic never leaves your machine. Also known as 'localhost'.",
        },
        {
            "question": "In the client-server model, which side initiates the connection?",
            "options": ["Server", "Client", "Both simultaneously", "The router"],
            "answer": 1,
            "explanation": "The client always initiates. The server sits and listens, then responds to incoming connections.",
        },
    ],
}


# ── Display ───────────────────────────────────────────────────────────────────

def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_question(number: int, total: int, q: dict, score: int, time_limit: int) -> None:
    clear()
    print(f"\n  Question {number}/{total}   Score: {score}   Time limit: {time_limit}s\n")
    print(f"  {q['question']}\n")
    for i, option in enumerate(q["options"]):
        print(f"    [{i + 1}] {option}")
    print()


# ── Quiz logic ────────────────────────────────────────────────────────────────

def run_quiz(questions: list[dict], time_limit: int = 15) -> tuple[int, int]:
    """
    Present each question in random order.
    Returns (score, total) as a tuple.
    The player has 'time_limit' seconds per question.
    """
    # random.sample returns a new shuffled list without modifying the original.
    shuffled = random.sample(questions, len(questions))
    score = 0
    total = len(shuffled)

    for i, q in enumerate(shuffled, 1):
        print_question(i, total, q, score, time_limit)
        start = time.time()

        try:
            raw = input("  Your answer (1-4): ").strip()
            elapsed = time.time() - start
        except KeyboardInterrupt:
            print("\n\n  Quiz interrupted.\n")
            return score, i - 1

        # Check time first — even a correct answer doesn't count if too slow.
        if elapsed > time_limit:
            print(f"\n  ⏰ Time's up! The answer was: {q['options'][q['answer']]}")
            print(f"  {q['explanation']}\n")
            input("  Press Enter to continue...")
            continue

        try:
            choice = int(raw) - 1   # convert to 0-based index
        except ValueError:
            choice = -1   # invalid input treated as wrong answer

        if choice == q["answer"]:
            # Bonus point for answering in under 5 seconds.
            bonus = 1 if elapsed < 5 else 0
            score += 1 + bonus
            bonus_msg = " (+1 speed bonus!)" if bonus else ""
            print(f"\n  ✓ Correct!{bonus_msg}  ({elapsed:.1f}s)")
        else:
            correct_text = q["options"][q["answer"]]
            print(f"\n  ✗ Wrong. Correct answer: {correct_text}")

        print(f"  💡 {q['explanation']}\n")
        input("  Press Enter to continue...")

    return score, total


def print_results(score: int, total: int, category: str) -> None:
    clear()
    max_possible = total * 2   # each question worth up to 2 points (1 + speed bonus)
    percentage = (score / max_possible) * 100 if max_possible > 0 else 0

    if percentage >= 80:
        grade, msg = "A", "Excellent work!"
    elif percentage >= 65:
        grade, msg = "B", "Good job!"
    elif percentage >= 50:
        grade, msg = "C", "Keep practicing."
    else:
        grade, msg = "F", "Review the material and try again."

    print(f"\n  ── Quiz Results: {category.upper()} ─────────────────────")
    print(f"  Score:      {score} / {max_possible} (speed bonuses included)")
    print(f"  Percentage: {percentage:.1f}%")
    print(f"  Grade:      {grade}  —  {msg}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    clear()
    print("\n╔══════════════════════════════════════╗")
    print("║            Quiz App CLI              ║")
    print("║   Jordi Yashua Contreras Blanch      ║")
    print("╚══════════════════════════════════════╝\n")
    print("  Answer within the time limit for full credit.")
    print("  Answer in under 5 seconds for a speed bonus point!\n")

    while True:
        print("  Category:  [1] Python   [2] Networking   [3] Mixed   [q] Quit\n")
        choice = input("  Choose: ").strip().lower()

        if choice == "q":
            print("\n  Thanks for studying! 📚\n")
            break
        elif choice == "1":
            questions = QUESTIONS["python"]
            category = "python"
        elif choice == "2":
            questions = QUESTIONS["networking"]
            category = "networking"
        elif choice == "3":
            # Combine both banks and pick 8 random questions.
            all_q = QUESTIONS["python"] + QUESTIONS["networking"]
            questions = random.sample(all_q, min(8, len(all_q)))
            category = "mixed"
        else:
            print("  Invalid option.\n")
            continue

        score, total = run_quiz(questions, time_limit=15)
        print_results(score, total, category)
        input("  Press Enter to return to menu...")
        clear()


if __name__ == "__main__":
    main()
