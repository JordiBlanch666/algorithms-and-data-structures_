# Hi, I'm Jordi Blanch 👋

**QA Analyst & Software Engineering Student** · Hybridge · Mexico

[![Email](https://img.shields.io/badge/paastor.blanch@gmail.com-EA4335?style=flat&logo=gmail&logoColor=white)](mailto:paastor.blanch@gmail.com)
[![GitHub](https://img.shields.io/badge/JordiBlanch666-181717?style=flat&logo=github&logoColor=white)](https://github.com/JordiBlanch666)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)

---

## About me

I'm not your typical first-semester CS student.

Before writing my first algorithm, I spent six years maintaining **zero-error metrics in live broadcast production** at K 102.7 FM — the closest real-world equivalent to a strict SLA. I designed **clinical decision algorithms in a hospital ICU** at San Jose Hospital, where documentation is non-negotiable and edge cases have consequences. At Charter Spectrum, I managed 50+ daily tickets using Jira and Zendesk while improving first-call resolution by 15%.

That background — broadcast ops, clinical QA, and enterprise tech support — is what brought me to Software Engineering. I'm formalizing what I already know about precision, documentation, and systems thinking into code.

This repository is where that transition lives.

---

## Repository structure

```
📦 primer-cuatrimestre-isw/
 ├── 📂 algoritmos/
 │   ├── 📂 ordenamiento/     ← Bubble, Selection, Insertion sort
 │   ├── 📂 busqueda/         ← Linear & Binary search
 │   └── 📂 recursion/        ← Factorial & Fibonacci (with memoization)
 ├── 📂 estructuras_datos/    ← Stack (LIFO) & Queue (FIFO)
 ├── 📂 fundamentos/          ← Functions, native data structures, file I/O
 └── 📂 proyectos/
     └── 📂 gestor_calificaciones/   ← CLI app with JSON persistence
```

---

## Algorithms

### Sorting

| Algorithm       | Best case | Average  | Worst case | Space |
|-----------------|:---------:|:--------:|:----------:|:-----:|
| Bubble Sort     | O(n)      | O(n²)    | O(n²)      | O(1)  |
| Selection Sort  | O(n²)     | O(n²)    | O(n²)      | O(1)  |
| Insertion Sort  | O(n)      | O(n²)    | O(n²)      | O(1)  |

### Searching

| Algorithm     | Complexity | Requires sorted input |
|---------------|:----------:|:---------------------:|
| Linear Search | O(n)       | No                    |
| Binary Search | O(log n)   | Yes                   |

### Recursion

- **Factorial** — base case + recursive call
- **Fibonacci** — naive O(2ⁿ) vs. memoized O(n) side by side

---

## Featured project — Grade Manager CLI

A command-line app to register and analyze student grades — built to demonstrate
functions, data structures, loops, conditionals, file I/O, and error handling in one coherent tool.

```bash
cd proyectos/gestor_calificaciones
python gestor.py
```

```
╔══════════════════════════════╗
║   Gestor de Calificaciones   ║
╚══════════════════════════════╝

  Alumno               Califs   Promedio  Letra
  -----------------------------------------------
  Ana García                3       88.3      B
  Carlos López              4       91.5      A
  María Martínez            2       74.0      C

  Class average: 84.6
```

**Concepts applied:**

| Concept            | Where                                      |
|--------------------|--------------------------------------------|
| Functions          | `load_data`, `calculate_average`, etc.     |
| Dict / List        | Student and grade storage                  |
| Loops              | Main menu loop, report rendering           |
| Conditionals       | Input validation, letter grade logic       |
| File I/O (JSON)    | Persistence with `json.load / json.dump`   |
| Error handling     | `try/except` on grade input                |

---

## Data Structures

| Structure | Type | Key operations         | Real-world demo              |
|-----------|------|------------------------|------------------------------|
| Stack     | LIFO | `push` / `pop`         | Balanced parentheses checker |
| Queue     | FIFO | `enqueue` / `dequeue`  | Service queue simulation     |

---

## What I learned this semester

- Analyzing time and space complexity of algorithms
- Implementing sorting and searching from scratch
- Recursion, memoization, and when each matters
- Designing custom data structures (Stack, Queue)
- File persistence with JSON and CSV
- Version control with Git & GitHub
- Unix/Linux terminal and CLI workflows

---

## Background

| Role              | Organization        | Relevant to SE                             |
|-------------------|---------------------|--------------------------------------------|
| QA / Broadcast Ops | K 102.7 FM         | Zero-error SLA, live system monitoring     |
| Clinical QA       | San Jose Hospital   | Algorithm design, validation, documentation |
| Tech Support      | Charter Spectrum    | Jira/Zendesk, ticket management, 15% FCR ↑ |

---

> *I show up. I document everything. I don't break things.*
> Currently finalizing a Software Engineering degree at Hybridge · Certified in Git/GitHub & n8n automation.

---

*Hybridge — Software Engineering · First semester · 2025–2026*
