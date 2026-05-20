"""
Portfolio — Jordi Yashua Contreras Blanch
Software Engineering · Hybridge

Runs demos from each portfolio module.
"""

import sys

# Windows terminals default to cp1252 which can't render box-drawing characters.
# This forces UTF-8 output so the portfolio menu displays correctly.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _pedir_lista() -> list:
    raw = input("\n  Ingresa tu lista separada por comas (ej: 45, 12, 78, 3, 56): ").strip()
    try:
        return [int(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError:
        print("  Lista inválida — solo números enteros separados por comas.")
        return []


def _bubble_steps(lst: list, verbose: bool) -> tuple:
    arr = lst.copy()
    n, comparaciones, intercambios, pasadas = len(arr), 0, 0, 0
    for i in range(n - 1):
        swapped = False
        pasadas += 1
        for j in range(n - 1 - i):
            comparaciones += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                intercambios += 1
                swapped = True
        if verbose:
            print(f"    Pasada {pasadas}: {arr}  (swap: {'sí' if swapped else 'no'})")
        if not swapped:
            break
    return arr, comparaciones, intercambios, pasadas


def _insertion_steps(lst: list, verbose: bool) -> tuple:
    arr = lst.copy()
    comparaciones, movimientos = 0, 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            comparaciones += 1
            arr[j + 1] = arr[j]
            movimientos += 1
            j -= 1
        arr[j + 1] = key
        if verbose:
            print(f"    Insertar {key:>4}: {arr}")
    return arr, comparaciones, movimientos


def _selection_steps(lst: list, verbose: bool) -> tuple:
    arr = lst.copy()
    n, comparaciones, intercambios = len(arr), 0, 0
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            comparaciones += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        if min_idx != i:
            intercambios += 1
        if verbose:
            print(f"    Mínimo → pos {i}: {arr}")
    return arr, comparaciones, intercambios


def _demo_sorting(data: list):
    verbose = input("\n  ¿Ver paso a paso? [s/n]: ").strip().lower() == "s"
    print(f"\n  Lista original: {data}\n")

    print("  ── Bubble Sort ──")
    res, comp, swaps, pasadas = _bubble_steps(data, verbose)
    print(f"  Resultado:      {res}")
    print(f"  Pasadas: {pasadas}  |  Comparaciones: {comp}  |  Intercambios: {swaps}\n")

    print("  ── Insertion Sort ──")
    res, comp, movs = _insertion_steps(data, verbose)
    print(f"  Resultado:  {res}")
    print(f"  Comparaciones: {comp}  |  Movimientos: {movs}\n")

    print("  ── Selection Sort ──")
    res, comp, swaps = _selection_steps(data, verbose)
    print(f"  Resultado:  {res}")
    print(f"  Comparaciones: {comp}  |  Intercambios: {swaps}")


def _demo_search(data: list):
    from algoritmos.busqueda.lineal import linear_search
    from algoritmos.busqueda.binaria import binary_search

    try:
        target = int(input("\n  ¿Qué número buscas? ").strip())
    except ValueError:
        print("  Número inválido.")
        return

    verbose = input("  ¿Ver paso a paso? [s/n]: ").strip().lower() == "s"
    print()

    # Búsqueda lineal
    pasos_lineal = 0
    idx_lineal = -1
    for i, val in enumerate(data):
        pasos_lineal += 1
        if verbose:
            marca = " ← ENCONTRADO" if val == target else ""
            print(f"    Lineal  [{i}] = {val}{marca}")
        if val == target:
            idx_lineal = i
            break

    if idx_lineal == -1 and verbose:
        print(f"    Lineal  — {target} no está en la lista")

    resultado_lineal = f"índice {idx_lineal}" if idx_lineal != -1 else "no encontrado"
    print(f"\n  Lineal:  {resultado_lineal}  ({pasos_lineal} comparaciones)")

    # Búsqueda binaria (requiere lista ordenada)
    sorted_data = sorted(data)
    left, right, pasos_binaria, idx_binaria = 0, len(sorted_data) - 1, 0, -1
    while left <= right:
        mid = (left + right) // 2
        pasos_binaria += 1
        if verbose:
            print(f"    Binaria [{left}..{right}] mid={mid} → {sorted_data[mid]}", end="")
        if sorted_data[mid] == target:
            idx_binaria = mid
            if verbose:
                print(" ← ENCONTRADO")
            break
        elif sorted_data[mid] < target:
            if verbose:
                print(" → buscar derecha")
            left = mid + 1
        else:
            if verbose:
                print(" → buscar izquierda")
            right = mid - 1

    resultado_binaria = f"índice {idx_binaria} en lista ordenada {sorted_data}" if idx_binaria != -1 else "no encontrado"
    print(f"  Binaria: {resultado_binaria}  ({pasos_binaria} comparaciones)")


def _demo_fibonacci():
    try:
        n = int(input("\n  Fibonacci(n) — ingresa n: ").strip())
    except ValueError:
        print("  Número inválido.")
        return

    verbose = input("  ¿Ver cada F(i) calculado? [s/n]: ").strip().lower() == "s"

    memo = {0: 0, 1: 1}

    def fib(k):
        if k in memo:
            return memo[k]
        memo[k] = fib(k - 1) + fib(k - 2)
        if verbose:
            print(f"    F({k}) = F({k-1}) + F({k-2}) = {memo[k-1]} + {memo[k-2]} = {memo[k]}")
        return memo[k]

    if verbose:
        print(f"    F(0) = 0  (base)")
        print(f"    F(1) = 1  (base)")
    secuencia = [fib(i) for i in range(n + 1)]
    print(f"\n  F(0) a F({n}): {secuencia}")
    print(f"  F({n}) = {secuencia[-1]}")


def demo_algorithms():
    data = _pedir_lista()
    if not data:
        return

    while True:
        print(f"\n  Tu lista: {data}")
        print("  [1] Ordenar — Bubble, Insertion, Selection")
        print("  [2] Buscar un valor")
        print("  [3] Fibonacci(n)")
        print("  [0] Volver")

        choice = input("\n  Opción: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            _demo_sorting(data)
        elif choice == "2":
            _demo_search(data)
        elif choice == "3":
            _demo_fibonacci()
        else:
            print("  Opción inválida.")


def demo_data_structures():
    from estructuras_datos.pila import Pila, verificar_parentesis
    from estructuras_datos.cola import Cola

    stack = Pila()
    for v in [10, 20, 30]:
        stack.push(v)
    print(f"  Stack: {stack}  → pop: {stack.pop()}")

    queue = Cola()
    for v in ["A", "B", "C"]:
        queue.enqueue(v)
    print(f"  Queue: {queue}  → dequeue: {queue.dequeue()}")

    expressions = ["(a + b) * [c]", "((x + y)", "{a + [b]}"]
    print("\n  Bracket validation:")
    for expr in expressions:
        status = "✓" if verificar_parentesis(expr) else "✗"
        print(f"    {status}  {expr}")


def demo_oop():
    from poo.herencia import SavingsAccount, CheckingAccount

    print("  — Savings Account —")
    savings = SavingsAccount("Jordi Blanch", 1000.0, interest_rate=0.05)
    savings.deposit(500)
    savings.apply_interest()
    print(savings)

    print("\n  — Checking Account —")
    checking = CheckingAccount("Ana García", 200.0, overdraft_limit=300.0)
    checking.withdraw(400)
    print(checking)


MODULES = {
    "1": ("Algorithms (sorting, searching, recursion)", demo_algorithms),
    "2": ("Data structures (Stack, Queue)",             demo_data_structures),
    "3": ("OOP — Banking System",                       demo_oop),
}


def main():
    print("\n╔══════════════════════════════════════════╗")
    print("║   Portfolio · Jordi Contreras Blanch    ║")
    print("║   Software Engineering · Hybridge       ║")
    print("╚══════════════════════════════════════════╝\n")

    for key, (name, _) in MODULES.items():
        print(f"  [{key}] {name}")
    print("  [0] Exit\n")

    choice = input("  Choose a module: ").strip()

    if choice == "0":
        sys.exit(0)

    if choice not in MODULES:
        print("  Invalid option.")
        return

    name, fn = MODULES[choice]
    print(f"\n── {name} ──────────────────────────────────\n")
    fn()
    print()


if __name__ == "__main__":
    main()
