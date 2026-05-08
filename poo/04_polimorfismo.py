"""
Polymorphism — fourth pillar of OOP.

Poly = many, morph = form. The same method name produces different behavior
depending on which object is calling it.

The real power: print_report() at the bottom of this file doesn't know
or care whether it receives a Circle, Rectangle, or Triangle. It just calls
.area() and .perimeter() and trusts that each shape knows how to compute them.
This means you can add a Hexagon class tomorrow and print_report() will work
with it without any changes.

ABC (Abstract Base Class) enforces the contract: any class that inherits
from Shape MUST implement area() and perimeter(). If it doesn't, Python
raises a TypeError the moment you try to instantiate it.
"""

from abc import ABC, abstractmethod
import math


class Shape(ABC):
    """
    Abstract base class — defines the interface, not the implementation.
    You cannot do Shape() directly. It exists only to be subclassed.
    """

    @abstractmethod
    def area(self) -> float:
        # @abstractmethod means "subclasses are required to implement this."
        # The ... (Ellipsis) is the conventional placeholder body for abstract methods.
        ...

    @abstractmethod
    def perimeter(self) -> float:
        ...

    def describe(self) -> str:
        # This is a CONCRETE method on the abstract class — all shapes share it.
        # It calls self.area() and self.perimeter(), which will resolve to
        # whichever subclass is actually running. That's polymorphism in action.
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
        # For a circle, perimeter == circumference
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
        # Heron's formula — works for any triangle given its three sides.
        # s is the semi-perimeter.
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self) -> float:
        return self.a + self.b + self.c


def print_report(shapes: list[Shape]) -> None:
    """
    This function is the clearest example of polymorphism in this file.
    It receives a list of Shape objects and calls .describe() on each one.
    It doesn't import Circle, Rectangle, or Triangle — it doesn't need to.
    The correct area/perimeter logic is dispatched automatically by Python
    based on each object's actual type at runtime.
    """
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
