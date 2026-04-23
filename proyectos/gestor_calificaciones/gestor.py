"""
Gestor de Calificaciones
Demuestra: funciones, estructuras de datos, archivos JSON,
           bucles, condicionales y manejo de errores.
"""

import json
import os

ARCHIVO_DATOS = os.path.join(os.path.dirname(__file__), "calificaciones.json")


# ── Persistencia ─────────────────────────────────────────────────────────────

def cargar_datos() -> dict:
    if not os.path.exists(ARCHIVO_DATOS):
        return {}
    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_datos(datos: dict) -> None:
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


# ── Lógica de negocio ─────────────────────────────────────────────────────────

def agregar_alumno(datos: dict, nombre: str) -> None:
    nombre = nombre.strip().title()
    if nombre in datos:
        print(f"  '{nombre}' ya existe.")
        return
    datos[nombre] = []
    guardar_datos(datos)
    print(f"  Alumno '{nombre}' agregado.")


def agregar_calificacion(datos: dict, nombre: str, calificacion: float) -> None:
    nombre = nombre.strip().title()
    if nombre not in datos:
        print(f"  Alumno '{nombre}' no encontrado.")
        return
    if not (0 <= calificacion <= 100):
        print("  La calificación debe estar entre 0 y 100.")
        return
    datos[nombre].append(calificacion)
    guardar_datos(datos)
    print(f"  Calificación {calificacion} registrada para '{nombre}'.")


def calcular_promedio(calificaciones: list) -> float:
    if not calificaciones:
        return 0.0
    return sum(calificaciones) / len(calificaciones)


def obtener_letra(promedio: float) -> str:
    if promedio >= 90:
        return "A"
    elif promedio >= 80:
        return "B"
    elif promedio >= 70:
        return "C"
    elif promedio >= 60:
        return "D"
    return "F"


def mostrar_reporte(datos: dict) -> None:
    if not datos:
        print("  No hay alumnos registrados.")
        return

    print(f"\n  {'Alumno':<20} {'Califs':>6} {'Promedio':>9} {'Letra':>6}")
    print("  " + "-" * 45)

    for nombre, califs in sorted(datos.items()):
        promedio = calcular_promedio(califs)
        letra = obtener_letra(promedio) if califs else "-"
        total = len(califs)
        print(f"  {nombre:<20} {total:>6} {promedio:>9.1f} {letra:>6}")

    promedios = [calcular_promedio(c) for c in datos.values() if c]
    if promedios:
        media_grupo = sum(promedios) / len(promedios)
        print(f"\n  Promedio del grupo: {media_grupo:.1f}")


# ── Interfaz CLI ──────────────────────────────────────────────────────────────

def menu() -> None:
    datos = cargar_datos()

    opciones = {
        "1": "Agregar alumno",
        "2": "Registrar calificación",
        "3": "Ver reporte",
        "4": "Salir",
    }

    print("\n╔══════════════════════════════╗")
    print("║   Gestor de Calificaciones   ║")
    print("╚══════════════════════════════╝")

    while True:
        print()
        for clave, descripcion in opciones.items():
            print(f"  [{clave}] {descripcion}")

        opcion = input("\n  Elige una opción: ").strip()

        if opcion == "1":
            nombre = input("  Nombre del alumno: ")
            agregar_alumno(datos, nombre)

        elif opcion == "2":
            nombre = input("  Nombre del alumno: ")
            try:
                calificacion = float(input("  Calificación (0-100): "))
                agregar_calificacion(datos, nombre, calificacion)
            except ValueError:
                print("  Ingresa un número válido.")

        elif opcion == "3":
            mostrar_reporte(datos)

        elif opcion == "4":
            print("\n  ¡Hasta luego!\n")
            break

        else:
            print("  Opción no válida.")


if __name__ == "__main__":
    menu()
