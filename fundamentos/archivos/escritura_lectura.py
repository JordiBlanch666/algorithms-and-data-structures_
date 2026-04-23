"""
Manejo de Archivos en Python
Demuestra lectura y escritura de archivos .txt y .csv.
"""

import csv
import os

DIRECTORIO = os.path.dirname(__file__)


# ── Archivos de texto ─────────────────────────────────────────────────────────

def escribir_txt(ruta: str, lineas: list) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        f.writelines(f"{linea}\n" for linea in lineas)
    print(f"Archivo '{ruta}' escrito ({len(lineas)} líneas).")


def leer_txt(ruta: str) -> list:
    with open(ruta, "r", encoding="utf-8") as f:
        return [linea.strip() for linea in f.readlines()]


# ── Archivos CSV ──────────────────────────────────────────────────────────────

def escribir_csv(ruta: str, encabezados: list, filas: list) -> None:
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        writer.writeheader()
        writer.writerows(filas)
    print(f"CSV '{ruta}' escrito ({len(filas)} registros).")


def leer_csv(ruta: str) -> list:
    with open(ruta, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # TXT
    notas = [
        "Algoritmos y Diseño — Aprobado",
        "Taller Git/GitHub  — Aprobado",
        "Experiencia de Usuario — En curso",
    ]
    ruta_txt = os.path.join(DIRECTORIO, "materias.txt")
    escribir_txt(ruta_txt, notas)
    contenido = leer_txt(ruta_txt)
    print("Leído:", contenido)

    # CSV
    alumnos = [
        {"nombre": "Ana García", "promedio": 9.5, "estado": "Activo"},
        {"nombre": "Carlos López", "promedio": 8.2, "estado": "Activo"},
        {"nombre": "María Martínez", "promedio": 7.8, "estado": "Activo"},
    ]
    ruta_csv = os.path.join(DIRECTORIO, "alumnos.csv")
    escribir_csv(ruta_csv, ["nombre", "promedio", "estado"], alumnos)

    registros = leer_csv(ruta_csv)
    print("\nRegistros CSV:")
    for r in registros:
        print(f"  {r['nombre']} → {r['promedio']}")
