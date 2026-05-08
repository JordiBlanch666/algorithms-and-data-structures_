"""
Stack — LIFO: Last In, First Out.

A stack is one of the most fundamental data structures in computer science.
Real-world analogies: a stack of plates, the browser back button, undo/redo.

The computer itself uses a call stack: every time you call a function, Python
pushes a frame onto the stack. When the function returns, it pops. That's why
infinite recursion causes a "RecursionError: maximum recursion depth exceeded" —
you fill up the call stack.

Key operations (all O(1)):
  push(x) — add to the top
  pop()   — remove from the top
  peek()  — look at the top without removing

We implement this with Python's list, which already has O(1) append and pop
at the end. Using the end as the "top" is important — inserting or removing
from the front of a list is O(n) because every element shifts.
"""

from collections import deque   # noqa: F401  (imported in case you want to swap)


class Stack:
    def __init__(self):
        self._data = []   # internal list — implementation detail, not public API

    def push(self, item) -> None:
        self._data.append(item)   # O(1) amortized

    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty.")
        return self._data.pop()   # O(1) — removes from the end

    def peek(self):
        """Return the top item without removing it."""
        if self.is_empty():
            raise IndexError("Stack is empty.")
        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"Stack({self._data})"


# ── Alias so existing code that imports 'Pila' still works ───────────────────
Pila = Stack


def check_brackets(expression: str) -> bool:
    """
    Real-world use case for a stack: validate that brackets are balanced.

    The algorithm:
      - Opening bracket → push it onto the stack.
      - Closing bracket → pop from the stack and check it matches.
      - At the end, the stack must be empty (every opener had a closer).

    This is how compilers check syntax — brackets, parentheses, braces.
    """
    stack = Stack()
    pairs = {")": "(", "]": "[", "}": "{"}

    for char in expression:
        if char in "([{":
            stack.push(char)
        elif char in ")]}":
            # If the stack is empty here, there's a closer with no opener.
            if stack.is_empty() or stack.pop() != pairs[char]:
                return False

    # If anything is left in the stack, there are unclosed openers.
    return stack.is_empty()


# Alias so existing code that imports 'verificar_parentesis' still works.
verificar_parentesis = check_brackets


if __name__ == "__main__":
    s = Stack()
    for val in [10, 20, 30]:
        s.push(val)
    print(s)
    print(f"Pop:  {s.pop()}")
    print(f"Peek: {s.peek()}")

    expressions = [
        ("(a + b) * [c - d]", True),
        ("((x + y)",          False),
        ("{a + [b * (c)]}",   True),
    ]
    print("\nBracket validation:")
    for expr, expected in expressions:
        result = check_brackets(expr)
        status = "✓" if result == expected else "✗ WRONG"
        print(f"  {status}  {expr!r}")
