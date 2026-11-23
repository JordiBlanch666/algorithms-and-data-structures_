"""
Functions in Python
Covers: parameters, default values, *args, **kwargs and lambdas.
"""


# ── Basic function ────────────────────────────────────────────────────────────

def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"


print(greet("Ana"))
print(greet("Carlos", "Good afternoon"))


# ── *args and **kwargs ────────────────────────────────────────────────────────

def add(*numbers: float) -> float:
    return sum(numbers)


def create_profile(name: str, **attributes) -> dict:
    return {"name": name, **attributes}


print(f"\nSum: {add(1, 2, 3, 4, 5)}")
print("Profile:", create_profile("Ana", age=20, major="Software Engineering", term=1))


# ── Higher-order functions ────────────────────────────────────────────────────

def apply(func, items: list) -> list:
    return [func(x) for x in items]


numbers = [1, 4, 9, 16, 25]
roots = apply(lambda x: x ** 0.5, numbers)
print(f"\nSquare roots of {numbers}:")
print([round(r, 2) for r in roots])


# ── Pure function vs. side effects ────────────────────────────────────────────

def celsius_to_fahrenheit(c: float) -> float:
    """Pure function: same input → same output, no external side effects."""
    return (c * 9 / 5) + 32


mexico_temperatures = [0, 15, 22, 30, 40]
print("\nMexico temperatures (°C → °F):")
for c in mexico_temperatures:
    print(f"  {c}°C = {celsius_to_fahrenheit(c):.1f}°F")
