"""
Factorial — recursion fundamentals.

Factorial(n) = n * (n-1) * (n-2) * ... * 1
Factorial(0) = 1  (by convention — the empty product)

Every recursive function needs two things:
  1. A BASE CASE that stops the recursion (n == 0 or n == 1 here).
     Without it, the function calls itself forever → RecursionError.
  2. A RECURSIVE CASE that moves toward the base case (n-1 gets smaller each call).

The iterative version is included for comparison. Both produce the same result,
but the iterative one uses O(1) space while the recursive one uses O(n) stack space
(one stack frame per call). For large n, the iterative version is safer.
"""


def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")

    # Base case: 0! = 1! = 1. This stops the chain of recursive calls.
    if n == 0 or n == 1:
        return 1

    # Recursive case: trust that factorial(n-1) is correct, multiply by n.
    # Python has to keep this call on the stack until factorial(n-1) returns.
    return n * factorial(n - 1)


def factorial_iterative(n: int) -> int:
    """Same result, O(1) space — no call stack buildup."""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


if __name__ == "__main__":
    print("n    recursive    iterative")
    print("-" * 30)
    for n in range(8):
        print(f"{n}    {factorial(n):<12} {factorial_iterative(n)}")
