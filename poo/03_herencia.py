"""
Inheritance — third pillar of OOP.

A child class inherits attributes and methods from the parent class,
and can extend or override them.
"""


class Animal:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species

    def describe(self) -> str:
        return f"{self.name} is a {self.species}"

    def make_sound(self) -> str:
        raise NotImplementedError("Each animal defines its own sound.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"


class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name, species="dog")
        self.breed = breed

    def make_sound(self) -> str:
        return "Woof!"

    def describe(self) -> str:
        base = super().describe()
        return f"{base}, breed: {self.breed}"


class Cat(Animal):
    def __init__(self, name: str, is_domestic: bool = True):
        super().__init__(name, species="cat")
        self.is_domestic = is_domestic

    def make_sound(self) -> str:
        return "Meow!"


class Parrot(Animal):
    def __init__(self, name: str, vocabulary: list[str]):
        super().__init__(name, species="parrot")
        self.vocabulary = vocabulary

    def make_sound(self) -> str:
        return f"{self.vocabulary[0]}!"

    def speak(self) -> str:
        return " — ".join(self.vocabulary)


if __name__ == "__main__":
    animals: list[Animal] = [
        Dog("Rex", "German Shepherd"),
        Cat("Michi"),
        Parrot("Paco", ["Hello", "Good morning", "I want water"]),
    ]

    print("── Inheritance: Animal hierarchy ───────────────")
    for a in animals:
        print(f"  {a!r:<25}  {a.describe()}")
        print(f"  {'':25}  Sound: {a.make_sound()}\n")
