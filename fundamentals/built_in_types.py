"""
Estructuras de Datos en Python
Ejemplos prácticos de listas, diccionarios, tuplas y conjuntos.
"""


# ── Listas ────────────────────────────────────────────────────────────────────

frutas = ["manzana", "banana", "cereza"]
frutas.append("mango")
frutas.insert(1, "fresa")
frutas.remove("banana")

print("Lista:", frutas)
print("Comprensión — frutas largas:", [f for f in frutas if len(f) > 5])


# ── Diccionarios ──────────────────────────────────────────────────────────────

estudiante = {
    "nombre": "Ana García",
    "carrera": "Ingeniería en Software",
    "semestre": 1,
    "materias": ["Algoritmos", "Cálculo", "Programación"],
}

print("\nEstudiante:", estudiante["nombre"])
print("Materias:", ", ".join(estudiante["materias"]))

estudiante["promedio"] = 9.2
print("Promedio agregado:", estudiante)


# ── Tuplas (inmutables) ───────────────────────────────────────────────────────

coordenadas = (19.4326, -99.1332)  # CDMX
latitud, longitud = coordenadas
print(f"\nCDMX → lat: {latitud}, lon: {longitud}")


# ── Conjuntos ─────────────────────────────────────────────────────────────────

lenguajes_a = {"Python", "JavaScript", "Java"}
lenguajes_b = {"Python", "Go", "Rust", "Java"}

print("\nEn ambos:", lenguajes_a & lenguajes_b)
print("En A pero no B:", lenguajes_a - lenguajes_b)
print("Unión:", lenguajes_a | lenguajes_b)
