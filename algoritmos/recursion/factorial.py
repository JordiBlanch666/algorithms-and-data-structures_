"""
Factorial con Recursión
Demuestra: caso base + llamada recursiva.
"""


def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("El factorial no está definido para negativos.")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def factorial_iterativo(n: int) -> int:
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado


if __name__ == "__main__":
    for num in range(8):
        print(f"{num}! = {factorial(num)}")
