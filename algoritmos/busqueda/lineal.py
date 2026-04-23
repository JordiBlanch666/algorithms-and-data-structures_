"""
Búsqueda Lineal (Linear Search)
Complejidad: O(n) tiempo | O(1) espacio
No requiere lista ordenada.
"""


def busqueda_lineal(lista: list, objetivo) -> int:
    """Retorna el índice del objetivo, o -1 si no existe."""
    for i, elemento in enumerate(lista):
        if elemento == objetivo:
            return i
    return -1


if __name__ == "__main__":
    numeros = [4, 2, 7, 1, 9, 3]
    objetivo = 7

    indice = busqueda_lineal(numeros, objetivo)
    if indice != -1:
        print(f"'{objetivo}' encontrado en el índice {indice}.")
    else:
        print(f"'{objetivo}' no está en la lista.")
