"""
Cola (Queue) — FIFO: First In, First Out
Implementación con collections.deque para operaciones O(1).
"""

from collections import deque


class Cola:
    def __init__(self):
        self._datos = deque()

    def encolar(self, elemento) -> None:
        self._datos.append(elemento)

    def desencolar(self):
        if self.esta_vacia():
            raise IndexError("La cola está vacía.")
        return self._datos.popleft()

    def frente(self):
        if self.esta_vacia():
            raise IndexError("La cola está vacía.")
        return self._datos[0]

    def esta_vacia(self) -> bool:
        return len(self._datos) == 0

    def __len__(self) -> int:
        return len(self._datos)

    def __repr__(self) -> str:
        return f"Cola({list(self._datos)})"


if __name__ == "__main__":
    # Simulación de fila de atención
    cola_atencion = Cola()
    clientes = ["Ana", "Carlos", "María", "Luis"]

    print("Clientes en espera:")
    for cliente in clientes:
        cola_atencion.encolar(cliente)
        print(f"  + {cliente} ingresó a la fila")

    print(f"\nAtendiendo ({len(cola_atencion)} en fila):")
    while not cola_atencion.esta_vacia():
        atendido = cola_atencion.desencolar()
        print(f"  ✓ {atendido} atendido/a")
