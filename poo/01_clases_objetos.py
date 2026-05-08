"""
Classes and Objects — first pillar of OOP.

A class is a blueprint; an object is an instance of that blueprint.
"""


class Product:
    # Class attribute: shared by all instances
    vat_rate = 0.16

    def __init__(self, name: str, price: float, quantity: int):
        self.name = name            # instance attribute
        self.price = price
        self.quantity = quantity

    def price_with_vat(self) -> float:
        return self.price * (1 + self.vat_rate)

    def inventory_value(self) -> float:
        return self.price_with_vat() * self.quantity

    def __repr__(self) -> str:
        return (
            f"Product('{self.name}', "
            f"price=${self.price:.2f}, "
            f"stock={self.quantity})"
        )


if __name__ == "__main__":
    laptop = Product("Laptop", 15_000.0, 5)
    mouse = Product("Mouse", 350.0, 20)

    for p in [laptop, mouse]:
        print(f"{p.name:<10}  price+VAT: ${p.price_with_vat():>9.2f}  "
              f"inventory: ${p.inventory_value():>11.2f}")
