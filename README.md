# Primer Cuatrimestre — Ingeniería en Software

Portfolio de algoritmos, estructuras de datos y proyectos desarrollados durante mi primer cuatrimestre en Hybridge.

## Sobre mí

Estudiante de **Ingeniería en Software** en Hybridge. Apasionado/a por resolver problemas con código limpio y bien estructurado. Actualmente dominando los fundamentos de algoritmos y Python.

---

## Estructura del repositorio

```
📦 primer-cuatrimestre/
 ├── 📂 algoritmos/
 │   ├── 📂 ordenamiento/     ← Burbuja, Selección, Inserción
 │   ├── 📂 busqueda/         ← Lineal y Binaria
 │   └── 📂 recursion/        ← Factorial y Fibonacci con memoización
 ├── 📂 estructuras_datos/    ← Pila (Stack) y Cola (Queue)
 ├── 📂 fundamentos/          ← Funciones, estructuras de datos nativas, archivos
 └── 📂 proyectos/
     └── 📂 gestor_calificaciones/   ← App CLI con persistencia JSON
```

---

## Algoritmos implementados

### Ordenamiento

| Algoritmo   | Mejor caso | Caso promedio | Peor caso | Espacio |
|-------------|:----------:|:-------------:|:---------:|:-------:|
| Burbuja     | O(n)       | O(n²)         | O(n²)     | O(1)    |
| Selección   | O(n²)      | O(n²)         | O(n²)     | O(1)    |
| Inserción   | O(n)       | O(n²)         | O(n²)     | O(1)    |

### Búsqueda

| Algoritmo  | Complejidad | Requiere orden |
|------------|:-----------:|:--------------:|
| Lineal     | O(n)        | No             |
| Binaria    | O(log n)    | Sí             |

### Recursión

- **Factorial** — caso base + llamada recursiva
- **Fibonacci** — comparación entre O(2ⁿ) recursivo y O(n) con memoización

---

## Proyecto principal

### Gestor de Calificaciones

App de línea de comandos para registrar y analizar calificaciones de alumnos.

**Características:**
- Registro de alumnos y calificaciones
- Cálculo automático de promedios y letra (A–F)
- Persistencia en archivo JSON
- Reporte tabular con estadísticas de grupo

```bash
cd proyectos/gestor_calificaciones
python gestor.py
```

---

## Estructuras de Datos

| Estructura | Tipo  | Operación principal       | Caso de uso real          |
|------------|-------|---------------------------|---------------------------|
| Pila       | LIFO  | `push` / `pop`            | Verificación de paréntesis |
| Cola       | FIFO  | `encolar` / `desencolar`  | Simulación de fila        |

---

## Stack tecnológico

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)

---

## Ejecutar cualquier módulo

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/primer-cuatrimestre-isw.git
cd primer-cuatrimestre-isw

# Ejecutar un algoritmo
python algoritmos/ordenamiento/burbuja.py

# Ejecutar el proyecto
python proyectos/gestor_calificaciones/gestor.py
```

> No requiere dependencias externas — solo Python 3.10+.

---

## Lo que aprendí este cuatrimestre

- Analizar complejidad temporal y espacial de algoritmos
- Implementar ordenamiento y búsqueda desde cero
- Trabajar con recursión y memoización
- Diseñar estructuras de datos (Pila, Cola)
- Persistencia de datos con archivos JSON y CSV
- Control de versiones con Git y GitHub
- Terminal Unix/Linux y flujo de trabajo con CLI

---

*Hybridge — Ingeniería en Software · Primer cuatrimestre · 2025–2026*
