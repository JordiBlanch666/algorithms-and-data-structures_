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


def demo_algorithms():
    from algoritmos.ordenamiento.burbuja import burbuja
    from algoritmos.ordenamiento.insercion import insercion
    from algoritmos.ordenamiento.seleccion import seleccion
    from algoritmos.busqueda.binaria import binaria
    from algoritmos.busqueda.lineal import lineal
    from algoritmos.recursion.fibonacci import fibonacci

    data = [64, 34, 25, 12, 22, 11, 90]
    print(f"  Original:          {data}")
    print(f"  Bubble sort:       {burbuja(data)}")
    print(f"  Insertion sort:    {insercion(data)}")
    print(f"  Selection sort:    {seleccion(data)}")

    sorted_data = sorted(data)
    print(f"\n  Linear search for 25:  index {lineal(data, 25)}")
    print(f"  Binary search for 25:  index {binaria(sorted_data, 25)}")
    print(f"\n  Fibonacci(10): {[fibonacci(i) for i in range(11)]}")


def demo_data_structures():
    from estructuras_datos.pila import Pila, verificar_parentesis
    from estructuras_datos.cola import Cola

    stack = Pila()
    for v in [10, 20, 30]:
        stack.push(v)
    print(f"  Stack: {stack}  → pop: {stack.pop()}")

    queue = Cola()
    for v in ["A", "B", "C"]:
        queue.encolar(v)
    print(f"  Queue: {queue}  → dequeue: {queue.desencolar()}")

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
