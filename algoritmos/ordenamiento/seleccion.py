"""
Ordenamiento por Selección (Selection Sort)
Complejidad: O(n²) tiempo | O(1) espacio
"""


def seleccion(lista: list) -> list:
    arr = lista.copy()
    n = len(arr)

    for i in range(n - 1):
        idx_min = i
        for j in range(i + 1, n):
            if arr[j] < arr[idx_min]:
                idx_min = j
        arr[i], arr[idx_min] = arr[idx_min], arr[i]

    return arr


if __name__ == "__main__":
    numeros = [29, 10, 14, 37, 13]
    print(f"Original:  {numeros}")
    print(f"Ordenado:  {seleccion(numeros)}")
