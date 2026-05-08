"""
Fibonacci — naive recursion vs. memoization.

Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21, ...
Each number is the sum of the two before it: F(n) = F(n-1) + F(n-2)

This file shows the same problem solved two ways to illustrate why
memoization matters:

NAIVE O(2^n): fibonacci_naive(30) makes over 1 million recursive calls.
              fibonacci_naive(50) would take years to finish.

MEMOIZED O(n): stores each result the first time it's computed. Any future
               call for the same n just looks up the stored answer instead
               of recomputing. This collapses the exponential tree into a
               straight line — O(n) time, O(n) space.

This pattern (cache expensive results to avoid redundant work) is called
dynamic programming. Memoization is the top-down approach.
"""


def fibonacci_naive(n: int) -> int:
    """
    Simple but exponentially slow. fibonacci_naive(n) calls itself
    roughly 2^n times because the same sub-problems get recomputed repeatedly.
    Only use this to demonstrate the problem — never in production.
    """
    if n <= 1:
        return n
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


def fibonacci_memo(n: int, memo: dict | None = None) -> int:
    """
    Memoized version. The memo dict acts as a cache: the first time we
    compute F(k), we store the result. Every subsequent call for F(k)
    returns immediately from the cache.
    """
    if memo is None:
        memo = {}   # fresh cache per top-level call
    if n <= 1:
        return n
    if n in memo:
        return memo[n]   # cache hit — skip the recursion entirely
    memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
    return memo[n]


# Default export used by main.py and other modules.
fibonacci = fibonacci_memo


if __name__ == "__main__":
    print("Fibonacci sequence (first 15 numbers):")
    sequence = [fibonacci_memo(i) for i in range(15)]
    print(sequence)

    print("\nNaive vs memoized — same results, very different speed:")
    print(f"  F(10) naive:    {fibonacci_naive(10)}")
    print(f"  F(10) memoized: {fibonacci_memo(10)}")
    print(f"  F(35) memoized: {fibonacci_memo(35)}  ← naive would take seconds")
