"""
Polymorphism — fourth pillar of OOP.

The same method can behave differently depending on the object that
implements it. The calling code doesn't need to know the concrete type.
"""

from abc import ABC, abstractmethod
import math


class Shape(ABC):
    """Abstract base class: defines the interface without implementing it."""

    @abstractmethod
    def area(self) -> float:
        ...

    @abstractmethod
    def perimeter(self) -> float:
        ...

    def describe(self) -> str:
        return (
            f"{self.__class__.__name__:<15} "
            f"area={self.area():>8.2f}  "
            f"perimeter={self.perimeter():>8.2f}"
        )


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, base: float, height: float):
        self.base = base
        self.height = height

    def area(self) -> float:
        return self.base * self.height

    def perimeter(self) -> float:
        return 2 * (self.base + self.height)


class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float):
        self.a, self.b, self.c = a, b, c

    def area(self) -> float:
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self) -> float:
        return self.a + self.b + self.c


def print_report(shapes: list[Shape]) -> None:
    """Polymorphic function: knows nothing about the concrete type."""
    print(f"  {'Shape':<15} {'Area':>12}  {'Perimeter':>14}")
    print("  " + "-" * 46)
    for s in shapes:
        print(f"  {s.describe()}")
    total = sum(s.area() for s in shapes)
    print(f"\n  Total area: {total:.2f}")


if __name__ == "__main__":
    shapes: list[Shape] = [
        Circle(5),
        Rectangle(4, 6),
        Triangle(3, 4, 5),
    ]

    print("── Polymorphism: shape report ───────────────────")
    print_report(shapes)
