"""
Búsqueda Binaria (Binary Search)
Complejidad: O(log n) tiempo | O(1) espacio
Requiere lista ordenada.
"""


def busqueda_binaria(lista: list, objetivo) -> int:
    """Retorna el índice del objetivo, o -1 si no existe."""
    izquierda, derecha = 0, len(lista) - 1

    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        if lista[medio] == objetivo:
            return medio
        elif lista[medio] < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1

    return -1


if __name__ == "__main__":
    numeros = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    objetivo = 23

    indice = busqueda_binaria(numeros, objetivo)
    if indice != -1:
        print(f"'{objetivo}' encontrado en el índice {indice}.")
    else:
        print(f"'{objetivo}' no está en la lista.")
