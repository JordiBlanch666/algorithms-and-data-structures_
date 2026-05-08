"""
Classes and Objects — first pillar of OOP.

A class is a blueprint that describes what an object will look like and
how it will behave. Every time you create an object from that class,
Python builds a fresh copy of the data defined in __init__.

The key insight: classes bundle DATA (attributes) and BEHAVIOR (methods)
together. That's what separates OOP from plain procedural code.
"""


class Product:
    # This is a CLASS attribute — it lives on the class itself, not on each
    # individual object. Every Product shares the same vat_rate unless you
    # explicitly override it on a specific instance. Good for constants that
    # apply to the whole category of objects.
    vat_rate = 0.16

    def __init__(self, name: str, price: float, quantity: int):
        # These are INSTANCE attributes — each Product object gets its own
        # copy. Changing laptop.name won't affect mouse.name.
        self.name = name
        self.price = price
        self.quantity = quantity

    def price_with_vat(self) -> float:
        # Methods receive 'self' so they can access the instance's own data.
        # We calculate on the fly instead of storing it — that way if price
        # ever changes, this method always returns the correct result.
        return self.price * (1 + self.vat_rate)

    def inventory_value(self) -> float:
        # Reusing price_with_vat() here instead of repeating the formula.
        # If VAT logic changes, we only fix one place.
        return self.price_with_vat() * self.quantity

    def __repr__(self) -> str:
        # __repr__ is what Python shows when you print an object or inspect
        # it in the REPL. Without it you'd see something like
        # <__main__.Product object at 0x...> which tells you nothing useful.
        return (
            f"Product('{self.name}', "
            f"price=${self.price:.2f}, "
            f"stock={self.quantity})"
        )


if __name__ == "__main__":
    # Creating two independent instances from the same blueprint.
    # Each one has its own name, price, and quantity.
    laptop = Product("Laptop", 15_000.0, 5)
    mouse = Product("Mouse", 350.0, 20)

    for p in [laptop, mouse]:
        print(f"{p.name:<10}  price+VAT: ${p.price_with_vat():>9.2f}  "
              f"inventory: ${p.inventory_value():>11.2f}")
