"""
Inheritance — third pillar of OOP.

Inheritance lets you define a general class (Animal) and then create
more specific versions (Dog, Cat, Parrot) that reuse everything the
parent defined — while still being free to add or override behavior.

The golden rule: use inheritance when the child IS-A parent.
  Dog IS-A Animal ✓   (good use of inheritance)
  Car HAS-A Engine ✗  (use composition instead)

super() is how a child talks to its parent. Calling super().__init__()
lets the parent set up its part of the object before the child adds its own.
"""


class Animal:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species

    def describe(self) -> str:
        return f"{self.name} is a {self.species}"

    def make_sound(self) -> str:
        # Raising NotImplementedError here signals to future developers:
        # "every subclass MUST override this." It's a lightweight contract
        # before we learned about abstract base classes (see file 04).
        raise NotImplementedError("Each animal defines its own sound.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"


class Dog(Animal):
    def __init__(self, name: str, breed: str):
        # super().__init__ handles name and species so we don't repeat that code.
        # We pass "dog" as the species — the parent stores it.
        super().__init__(name, species="dog")
        self.breed = breed   # Dog-specific attribute the parent doesn't have

    def make_sound(self) -> str:
        # Overriding the parent's method with Dog-specific behavior.
        return "Woof!"

    def describe(self) -> str:
        # We extend the parent's describe() instead of replacing it entirely.
        # super().describe() gives us "Rex is a dog", then we tack on the breed.
        base = super().describe()
        return f"{base}, breed: {self.breed}"


class Cat(Animal):
    def __init__(self, name: str, is_domestic: bool = True):
        super().__init__(name, species="cat")
        self.is_domestic = is_domestic

    def make_sound(self) -> str:
        return "Meow!"

    # Cat doesn't override describe() — it inherits it unchanged from Animal.
    # That's fine. Inheritance doesn't mean you MUST override everything.


class Parrot(Animal):
    def __init__(self, name: str, vocabulary: list[str]):
        super().__init__(name, species="parrot")
        self.vocabulary = vocabulary

    def make_sound(self) -> str:
        # Parrots repeat words, so we take the first one from their vocabulary.
        return f"{self.vocabulary[0]}!"

    def speak(self) -> str:
        # Extra method that only Parrots have — Animals in general can't do this.
        return " — ".join(self.vocabulary)


if __name__ == "__main__":
    # We store different subclass instances in a list typed as list[Animal].
    # This works because Dog, Cat, and Parrot are all Animals (IS-A relationship).
    animals: list[Animal] = [
        Dog("Rex", "German Shepherd"),
        Cat("Michi"),
        Parrot("Paco", ["Hello", "Good morning", "I want water"]),
    ]

    print("── Inheritance: Animal hierarchy ───────────────")
    for a in animals:
        # Each object responds to describe() and make_sound() in its own way,
        # even though we're calling the same method names on all of them.
        # That's polymorphism starting to show — covered in the next file.
        print(f"  {a!r:<25}  {a.describe()}")
        print(f"  {'':25}  Sound: {a.make_sound()}\n")
