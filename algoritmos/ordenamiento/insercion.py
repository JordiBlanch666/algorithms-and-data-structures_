"""
Ordenamiento por Inserción (Insertion Sort)
Complejidad: O(n²) peor caso | O(n) mejor caso | O(1) espacio
Eficiente para listas pequeñas o casi ordenadas.
"""


def insercion(lista: list) -> list:
    arr = lista.copy()

    for i in range(1, len(arr)):
        clave = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > clave:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = clave

    return arr


if __name__ == "__main__":
    numeros = [12, 11, 13, 5, 6]
    print(f"Original:  {numeros}")
    print(f"Ordenado:  {insercion(numeros)}")
