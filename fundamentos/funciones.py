"""
Funciones en Python
Cubre: parámetros, valores por defecto, *args, **kwargs y lambdas.
"""

from typing import Optional


# ── Función básica ────────────────────────────────────────────────────────────

def saludar(nombre: str, saludo: str = "Hola") -> str:
    return f"{saludo}, {nombre}!"


print(saludar("Ana"))
print(saludar("Carlos", "Buenas tardes"))


# ── *args y **kwargs ──────────────────────────────────────────────────────────

def suma(*numeros: float) -> float:
    return sum(numeros)


def crear_perfil(nombre: str, **atributos) -> dict:
    return {"nombre": nombre, **atributos}


print(f"\nSuma: {suma(1, 2, 3, 4, 5)}")
print("Perfil:", crear_perfil("Ana", edad=20, carrera="ISW", semestre=1))


# ── Funciones de orden superior ───────────────────────────────────────────────

def aplicar(funcion, lista: list) -> list:
    return [funcion(x) for x in lista]


numeros = [1, 4, 9, 16, 25]
raices = aplicar(lambda x: x ** 0.5, numeros)
print(f"\nRaíces de {numeros}:")
print([round(r, 2) for r in raices])


# ── Función pura vs con efectos ───────────────────────────────────────────────

def celsius_a_fahrenheit(c: float) -> float:
    """Función pura: mismo input → mismo output, sin efectos externos."""
    return (c * 9 / 5) + 32


temperaturas_mx = [0, 15, 22, 30, 40]
print("\nTemperaturas México (°C → °F):")
for c in temperaturas_mx:
    print(f"  {c}°C = {celsius_a_fahrenheit(c):.1f}°F")
