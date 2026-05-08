"""
Polimorfismo — cuarto pilar de la POO.

El mismo método puede tener comportamientos distintos según el objeto
que lo implementa. El código cliente no necesita saber el tipo concreto.
"""

from abc import ABC, abstractmethod
import math


class Figura(ABC):
    """Clase base abstracta: define la interfaz sin implementar."""

    @abstractmethod
    def area(self) -> float:
        ...

    @abstractmethod
    def perimetro(self) -> float:
        ...

    def describir(self) -> str:
        return (
            f"{self.__class__.__name__:<15} "
            f"área={self.area():>8.2f}  "
            f"perímetro={self.perimetro():>8.2f}"
        )


class Circulo(Figura):
    def __init__(self, radio: float):
        self.radio = radio

    def area(self) -> float:
        return math.pi * self.radio ** 2

    def perimetro(self) -> float:
        return 2 * math.pi * self.radio


class Rectangulo(Figura):
    def __init__(self, base: float, altura: float):
        self.base = base
        self.altura = altura

    def area(self) -> float:
        return self.base * self.altura

    def perimetro(self) -> float:
        return 2 * (self.base + self.altura)


class Triangulo(Figura):
    def __init__(self, a: float, b: float, c: float):
        self.a, self.b, self.c = a, b, c

    def area(self) -> float:
        s = self.perimetro() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimetro(self) -> float:
        return self.a + self.b + self.c


def imprimir_reporte(figuras: list[Figura]) -> None:
    """Función polimórfica: no sabe nada del tipo concreto."""
    print(f"  {'Figura':<15} {'Área':>12}  {'Perímetro':>14}")
    print("  " + "-" * 46)
    for f in figuras:
        print(f"  {f.describir()}")
    total = sum(f.area() for f in figuras)
    print(f"\n  Área total: {total:.2f}")


if __name__ == "__main__":
    figuras: list[Figura] = [
        Circulo(5),
        Rectangulo(4, 6),
        Triangulo(3, 4, 5),
    ]

    print("── Polimorfismo: reporte de figuras ────────────")
    imprimir_reporte(figuras)
