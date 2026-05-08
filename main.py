"""
Portafolio — Jordi Yashua Contreras Blanch
Ingeniería en Software · Hybridge

Ejecuta las demos de cada módulo del portafolio.
"""

import sys


def demo_algoritmos():
    from algoritmos.ordenamiento.burbuja import burbuja
    from algoritmos.ordenamiento.insercion import insercion
    from algoritmos.ordenamiento.seleccion import seleccion
    from algoritmos.busqueda.binaria import binaria
    from algoritmos.busqueda.lineal import lineal
    from algoritmos.recursion.fibonacci import fibonacci

    datos = [64, 34, 25, 12, 22, 11, 90]
    print(f"  Original:         {datos}")
    print(f"  Burbuja:          {burbuja(datos)}")
    print(f"  Inserción:        {insercion(datos)}")
    print(f"  Selección:        {seleccion(datos)}")

    ordenado = sorted(datos)
    print(f"\n  Búsqueda lineal de 25:  índice {lineal(datos, 25)}")
    print(f"  Búsqueda binaria de 25: índice {binaria(ordenado, 25)}")
    print(f"\n  Fibonacci(10): {[fibonacci(i) for i in range(11)]}")


def demo_estructuras():
    from estructuras_datos.pila import Pila, verificar_parentesis
    from estructuras_datos.cola import Cola

    p = Pila()
    for v in [10, 20, 30]:
        p.push(v)
    print(f"  Pila:  {p}  → pop: {p.pop()}")

    c = Cola()
    for v in ["A", "B", "C"]:
        c.encolar(v)
    print(f"  Cola:  {c}  → dequeue: {c.desencolar()}")

    casos = ["(a + b) * [c]", "((x + y)", "{a + [b]}"]
    print("\n  Verificación de paréntesis:")
    for expr in casos:
        estado = "✓" if verificar_parentesis(expr) else "✗"
        print(f"    {estado}  {expr}")


def demo_poo():
    from poo.herencia import CuentaAhorro, CuentaCorriente

    print("  — Cuenta de Ahorro —")
    ahorro = CuentaAhorro("Jordi Blanch", 1000.0, tasa_interes=0.05)
    ahorro.depositar(500)
    ahorro.aplicar_interes()
    print(ahorro)

    print("\n  — Cuenta Corriente —")
    corriente = CuentaCorriente("Ana García", 200.0, limite_sobregiro=300.0)
    corriente.retirar(400)
    print(corriente)


MODULOS = {
    "1": ("Algoritmos (ordenamiento, búsqueda, recursión)", demo_algoritmos),
    "2": ("Estructuras de datos (Pila, Cola)",             demo_estructuras),
    "3": ("POO — Sistema Bancario",                        demo_poo),
}


def main():
    print("\n╔══════════════════════════════════════════╗")
    print("║   Portafolio · Jordi Contreras Blanch   ║")
    print("║   Ingeniería en Software · Hybridge     ║")
    print("╚══════════════════════════════════════════╝\n")

    for clave, (nombre, _) in MODULOS.items():
        print(f"  [{clave}] {nombre}")
    print("  [0] Salir\n")

    opcion = input("  Elige un módulo: ").strip()

    if opcion == "0":
        sys.exit(0)

    if opcion not in MODULOS:
        print("  Opción no válida.")
        return

    nombre, fn = MODULOS[opcion]
    print(f"\n── {nombre} ──────────────────────────────────\n")
    fn()
    print()


if __name__ == "__main__":
    main()
