# Hi, I'm Jordi Blanch 👋

**QA Analyst & Software Engineering Student** · Hybridge · Mexico

[![Email](https://img.shields.io/badge/paastor.blanch@gmail.com-EA4335?style=flat&logo=gmail&logoColor=white)](mailto:paastor.blanch@gmail.com)
[![GitHub](https://img.shields.io/badge/JordiBlanch666-181717?style=flat&logo=github&logoColor=white)](https://github.com/JordiBlanch666)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)
![Semester](https://img.shields.io/badge/2nd%20semester-OOP-6A0DAD?style=flat)

---

## About me

I'm not your typical second-semester CS student.

Before writing my first algorithm, I spent six years maintaining **zero-error metrics in live broadcast production** at K 102.7 FM — the closest real-world equivalent to a strict SLA. I designed **clinical decision algorithms in a hospital ICU** at San Jose Hospital, where documentation is non-negotiable and edge cases have consequences. At Charter Spectrum, I managed 50+ daily tickets using Jira and Zendesk while improving first-call resolution by 15%.

That background — broadcast ops, clinical QA, and enterprise tech support — is what brought me to Software Engineering. I'm formalizing what I already know about precision, documentation, and systems thinking into code.

This repository tracks that transition, semester by semester.

---

## Repository structure

```
📦 algorithms-and-data-structures/
 ├── 📂 algoritmos/
 │   ├── 📂 ordenamiento/        ← Bubble, Selection, Insertion sort
 │   ├── 📂 busqueda/            ← Linear & Binary search
 │   └── 📂 recursion/           ← Factorial & Fibonacci (with memoization)
 ├── 📂 estructuras_datos/       ← Stack (LIFO) & Queue (FIFO)
 ├── 📂 fundamentos/             ← Functions, native data structures, file I/O
 ├── 📂 poo/                     ← OOP: the four pillars + banking system ⬅ new
 └── 📂 proyectos/
     └── 📂 gestor_calificaciones/   ← CLI app with JSON persistence
```

Run the full portfolio demo from the root:

```bash
python main.py
```

```
╔══════════════════════════════════════════╗
║   Portfolio · Jordi Contreras Blanch    ║
║   Software Engineering · Hybridge       ║
╚══════════════════════════════════════════╝

  [1] Algorithms (sorting, searching, recursion)
  [2] Data structures (Stack, Queue)
  [3] OOP — Banking System
  [0] Exit
```

---

## OOP — Second Semester

Four pillars, four files, one integrating project.

| File | Concept | Demo |
|------|---------|------|
| `poo/01_clases_objetos.py` | Classes & objects | Product catalog with VAT |
| `poo/02_encapsulacion.py` | Encapsulation | Bank account with private attributes |
| `poo/03_herencia.py` | Inheritance + `super()` | Animal → Dog / Cat / Parrot hierarchy |
| `poo/04_polimorfismo.py` | Polymorphism + ABC | Geometric shapes with a common interface |

### Featured OOP Project — Banking System

A cohesive example that combines all four pillars:

```
Account (ABC)              ← abstract class, encapsulation
├── SavingsAccount         ← inheritance, applies interest
└── CheckingAccount        ← inheritance, overdraft limit
```

```bash
python poo/herencia.py
```

```
══ Banking System ══════════════════════════════════

Savings | MX00001 | Jordi Blanch | balance: $1,365.00

  History:
    [10:32:01] Account opened with initial balance $1000.00
    [10:32:01] Deposit    +$    500.00  →  balance $1500.00
    [10:32:01] Withdraw   -$    200.00  →  balance $1300.00
    [10:32:01] Deposit    +$     65.00  →  balance $1365.00
```

**Concepts applied:**

| Concept | Where |
|---------|-------|
| Encapsulation | `__balance` only modified via `deposit` / `withdraw` |
| Inheritance | `SavingsAccount` and `CheckingAccount` extend `Account` |
| Polymorphism | `withdraw()` behaves differently in each subclass |
| Abstraction | `Account` is abstract — cannot be instantiated directly |
| `super()` | Child constructor delegates initialization to parent |
| `@property` | Read-only balance exposed cleanly |

---

## Algorithms — First Semester

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
║      Grade Manager CLI       ║
╚══════════════════════════════╝

  Student              Grades   Average   Grade
  -----------------------------------------------
  Ana García                3      88.3       B
  Carlos López              4      91.5       A
  María Martínez            2      74.0       C

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

## What I've learned

**Second semester (current)**
- OOP: classes, encapsulation, inheritance, polymorphism
- Abstract base classes (`ABC`, `@abstractmethod`)
- Properties, dunder methods, class vs. instance attributes
- Designing with object hierarchies

**First semester**
- Time and space complexity analysis
- Sorting and searching algorithms from scratch
- Recursion and memoization
- Custom data structures (Stack, Queue)
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
> Currently completing a Software Engineering degree at Hybridge · Certified in Git/GitHub & n8n automation.

---

*Hybridge — Software Engineering · Second semester · 2025–2026*
