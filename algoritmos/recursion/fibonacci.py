"""
Secuencia de Fibonacci con Recursión + Memoización
Demuestra cómo la memoización convierte O(2^n) en O(n).
"""


def fibonacci_recursivo(n: int) -> int:
    """Implementación simple O(2^n) — muestra el problema sin memo."""
    if n <= 1:
        return n
    return fibonacci_recursivo(n - 1) + fibonacci_recursivo(n - 2)


def fibonacci_memo(n: int, memo: dict = None) -> int:
    """Implementación con memoización O(n)."""
    if memo is None:
        memo = {}
    if n <= 1:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
    return memo[n]


if __name__ == "__main__":
    print("Primeros 10 números de Fibonacci:")
    secuencia = [fibonacci_memo(i) for i in range(10)]
    print(secuencia)
