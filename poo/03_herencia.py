"""
Herencia — tercer pilar de la POO.

Una clase hija hereda atributos y métodos de la clase padre,
y puede extenderlos o sobreescribirlos.
"""


class Animal:
    def __init__(self, nombre: str, especie: str):
        self.nombre = nombre
        self.especie = especie

    def describir(self) -> str:
        return f"{self.nombre} es un {self.especie}"

    def hacer_sonido(self) -> str:
        raise NotImplementedError("Cada animal define su propio sonido.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.nombre}')"


class Perro(Animal):
    def __init__(self, nombre: str, raza: str):
        super().__init__(nombre, especie="perro")
        self.raza = raza

    def hacer_sonido(self) -> str:
        return "¡Guau!"

    def describir(self) -> str:
        base = super().describir()
        return f"{base} de raza {self.raza}"


class Gato(Animal):
    def __init__(self, nombre: str, es_domestico: bool = True):
        super().__init__(nombre, especie="gato")
        self.es_domestico = es_domestico

    def hacer_sonido(self) -> str:
        return "¡Miau!"


class Loro(Animal):
    def __init__(self, nombre: str, vocabulario: list[str]):
        super().__init__(nombre, especie="loro")
        self.vocabulario = vocabulario

    def hacer_sonido(self) -> str:
        return f"¡{self.vocabulario[0]}!"

    def hablar(self) -> str:
        return " — ".join(self.vocabulario)


if __name__ == "__main__":
    animales: list[Animal] = [
        Perro("Rex", "Pastor Alemán"),
        Gato("Michi"),
        Loro("Paco", ["Hola", "Buenos días", "Quiero agua"]),
    ]

    print("── Herencia: jerarquía Animal ──────────────────")
    for a in animales:
        print(f"  {a!r:<25}  {a.describir()}")
        print(f"  {'':25}  Sonido: {a.hacer_sonido()}\n")
