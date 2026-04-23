"""
Pila (Stack) — LIFO: Last In, First Out
Implementación con lista de Python.
"""


class Pila:
    def __init__(self):
        self._datos = []

    def push(self, elemento) -> None:
        self._datos.append(elemento)

    def pop(self):
        if self.esta_vacia():
            raise IndexError("La pila está vacía.")
        return self._datos.pop()

    def peek(self):
        if self.esta_vacia():
            raise IndexError("La pila está vacía.")
        return self._datos[-1]

    def esta_vacia(self) -> bool:
        return len(self._datos) == 0

    def __len__(self) -> int:
        return len(self._datos)

    def __repr__(self) -> str:
        return f"Pila({self._datos})"


def verificar_parentesis(expresion: str) -> bool:
    """Ejemplo real: verifica que los paréntesis estén balanceados."""
    pila = Pila()
    pares = {")": "(", "]": "[", "}": "{"}

    for char in expresion:
        if char in "([{":
            pila.push(char)
        elif char in ")]}":
            if pila.esta_vacia() or pila.pop() != pares[char]:
                return False

    return pila.esta_vacia()


if __name__ == "__main__":
    p = Pila()
    for val in [10, 20, 30]:
        p.push(val)
    print(p)
    print("Pop:", p.pop())
    print("Peek:", p.peek())

    expresiones = ["(a + b) * [c - d]", "((x + y)", "{a + [b * (c)]}"]
    print("\nVerificación de paréntesis:")
    for expr in expresiones:
        resultado = "OK" if verificar_parentesis(expr) else "ERROR"
        print(f"  {expr!r:35} → {resultado}")
