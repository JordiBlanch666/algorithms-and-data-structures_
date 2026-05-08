"""
Clases y Objetos — primer pilar de la POO.

Una clase es una plantilla; un objeto es una instancia de esa plantilla.
"""


class Producto:
    # Atributo de clase: compartido por todas las instancias
    iva = 0.16

    def __init__(self, nombre: str, precio: float, cantidad: int):
        self.nombre = nombre        # atributo de instancia
        self.precio = precio
        self.cantidad = cantidad

    def precio_con_iva(self) -> float:
        return self.precio * (1 + self.iva)

    def valor_inventario(self) -> float:
        return self.precio_con_iva() * self.cantidad

    def __repr__(self) -> str:
        return (
            f"Producto('{self.nombre}', "
            f"precio=${self.precio:.2f}, "
            f"stock={self.cantidad})"
        )


if __name__ == "__main__":
    laptop = Producto("Laptop", 15_000.0, 5)
    mouse = Producto("Mouse", 350.0, 20)

    for p in [laptop, mouse]:
        print(f"{p.nombre:<10}  precio+IVA: ${p.precio_con_iva():>9.2f}  "
              f"inventario: ${p.valor_inventario():>11.2f}")
