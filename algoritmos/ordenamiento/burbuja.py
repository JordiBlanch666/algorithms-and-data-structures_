"""
Ordenamiento Burbuja (Bubble Sort)
Complejidad: O(n²) tiempo | O(1) espacio
"""


def burbuja(lista: list) -> list:
    arr = lista.copy()
    n = len(arr)

    for i in range(n - 1):
        intercambio = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                intercambio = True
        if not intercambio:
            break

    return arr


if __name__ == "__main__":
    numeros = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original:  {numeros}")
    print(f"Ordenado:  {burbuja(numeros)}")
