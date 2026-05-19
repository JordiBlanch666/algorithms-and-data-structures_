# Hi, I'm Jordi Blanch 👋

**QA Analyst & Software Engineering Student** · Hybridge · Mexico

[![Email](https://img.shields.io/badge/paastor.blanch@gmail.com-EA4335?style=flat&logo=gmail&logoColor=white)](mailto:paastor.blanch@gmail.com)
[![GitHub](https://img.shields.io/badge/JordiBlanch666-181717?style=flat&logo=github&logoColor=white)](https://github.com/JordiBlanch666)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)
![Semester](https://img.shields.io/badge/2nd%20semester-OOP%20%26%20Networking-6A0DAD?style=flat)

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
 ├── 📂 poo/                     ← OOP: the four pillars + banking system
 ├── 📂 redes/                   ← Networking: DNS, TCP, HTTP, port scanner
 └── 📂 proyectos/
     ├── 📂 calculadora/         ← Calculator with history & memory  ⬅ new
     ├── 📂 todo_app/            ← To-Do app with priorities & JSON  ⬅ new
     ├── 📂 hangman/             ← Hangman game with ASCII art       ⬅ new
     ├── 📂 quiz/                ← Quiz app with timer & categories  ⬅ new
     └── 📂 gestor_calificaciones/ ← Grade Manager CLI
```

Run the full portfolio demo from the root:

```bash
python main.py
```

---

## Projects

### Calculator CLI
> `proyectos/calculadora/calculadora.py`

A command-line calculator with operation history, memory register, and safe expression parsing — no `eval()` used.

```bash
python proyectos/calculadora/calculadora.py
```

```
  calc › 125 * 8
  = 1000

  calc [M=1000] › 1000 / 3
  = 333.33333333

  calc › history
  #    Operation                      Result
  --------------------------------------------------
  1    125 * 8 = 1000
  2    1000 / 3 = 333.33333333
```

| Concept | Where |
|---------|-------|
| Input parsing | `parse_expression()` splits and validates tokens |
| Error handling | `ZeroDivisionError`, `ValueError` caught gracefully |
| State | history list + memory float persist across operations |
| No `eval()` | explicit `if/elif` per operator — safe and readable |

---

### To-Do App CLI
> `proyectos/todo_app/todo.py`

Task manager with three priority levels, status filters, and JSON persistence. Data survives between sessions.

```bash
python proyectos/todo_app/todo.py
```

```
  todo › add Fix binary search bug -p high
  ✓ Added [1] 'Fix binary search bug' (high)

  todo › add Read OOP chapter
  ✓ Added [2] 'Read OOP chapter' (medium)

  todo › list pending
  ID   St  Pri      Title                               Created
  ────────────────────────────────────────────────────────────────────
  1    ○   🔴 high  Fix binary search bug               2025-05-19 10:00
  2    ○   🟡 med   Read OOP chapter                    2025-05-19 10:01
```

| Concept | Where |
|---------|-------|
| CRUD | `add_task`, `complete_task`, `delete_task` |
| Filtering & sorting | `filter_tasks()` by status and priority |
| JSON persistence | `load_tasks` / `save_tasks` on every change |
| ID generation | `next_id()` — max existing ID + 1 |

---

### Hangman
> `proyectos/hangman/hangman.py`

Classic word-guessing game with ASCII art gallows, three difficulty levels, and a built-in word bank.

```bash
python proyectos/hangman/hangman.py
```

```
       -----
       |   |
       |   O
       |  /|
       |
       |
    --------

  Difficulty: MEDIUM  |  Wrong guesses left: 3

  p y _ _ _ _

  Wrong letters: a e i o s
```

| Concept | Where |
|---------|-------|
| Sets | `guessed` and `wrong` for O(1) membership checks |
| String masking | `masked_word()` replaces unguessed letters with `_` |
| Game loop | `play_round()` handles win/loss conditions |
| ASCII art | 7 gallows stages indexed by wrong-guess count |

---

### Quiz App CLI
> `proyectos/quiz/quiz.py`

Multiple-choice quiz on Python fundamentals and Networking basics. 15-second timer per question, speed bonus for answers under 5 seconds.

```bash
python proyectos/quiz/quiz.py
```

```
  Question 3/8   Score: 4   Time limit: 15s

  What is the time complexity of accessing an element in a Python list by index?

    [1] O(n)
    [2] O(log n)
    [3] O(1)
    [4] O(n²)

  Your answer (1-4): 3
  ✓ Correct! (+1 speed bonus!)  (2.3s)
  💡 Lists store elements in contiguous memory, so index access is always O(1).
```

| Concept | Where |
|---------|-------|
| Randomization | `random.sample()` shuffles questions each run |
| Timer | `time.time()` measures response time per question |
| Speed bonus | extra point for answering in under 5 seconds |
| Score grading | percentage → A/B/C/F with feedback message |

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

```
Account (ABC)              ← abstract class, encapsulation
├── SavingsAccount         ← inheritance, applies interest
└── CheckingAccount        ← inheritance, overdraft limit
```

```bash
python poo/herencia.py
```

| Concept | Where |
|---------|-------|
| Encapsulation | `__balance` only modified via `deposit` / `withdraw` |
| Inheritance | `SavingsAccount` and `CheckingAccount` extend `Account` |
| Polymorphism | `withdraw()` behaves differently in each subclass |
| Abstraction | `Account` is abstract — cannot be instantiated directly |
| `super()` | Child constructor delegates initialization to parent |
| `@property` | Read-only balance exposed cleanly |

---

## Networking Fundamentals — Second Semester

| File | Concept | What it does |
|------|---------|--------------|
| `redes/01_network_info.py` | DNS & IP addressing | Resolves hostnames, reverse lookup |
| `redes/02_tcp_client_server.py` | TCP sockets | Echo server + client over localhost |
| `redes/03_http_client.py` | HTTP protocol | Real GET requests, status codes, JSON API |
| `redes/04_port_scanner.py` | Ports & services | Concurrent scanner with thread pool |

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

- **Factorial** — base case + recursive call, O(n) stack space vs O(1) iterative
- **Fibonacci** — naive O(2ⁿ) vs. memoized O(n) side by side

---

## Data Structures

| Structure | Type | Key operations     | Real-world demo              |
|-----------|------|--------------------|------------------------------|
| Stack     | LIFO | `push` / `pop`     | Balanced parentheses checker |
| Queue     | FIFO | `enqueue`/`dequeue`| Service queue simulation     |

---

## What I've learned

**Second semester (current)**
- OOP: classes, encapsulation, inheritance, polymorphism
- Abstract base classes (`ABC`, `@abstractmethod`)
- Properties, dunder methods, class vs. instance attributes
- Designing with object hierarchies
- Networking: IP addressing, DNS, TCP sockets, HTTP, port scanning
- Concurrency: `ThreadPoolExecutor` for parallel I/O tasks
- CLI app design: REPL loops, input validation, JSON persistence, CRUD

**First semester**
- Time and space complexity analysis
- Sorting and searching algorithms from scratch
- Recursion and memoization
- Custom data structures (Stack, Queue)
- File persistence with JSON
- Version control with Git & GitHub

---

## Background

| Role               | Organization      | Relevant to SE                              |
|--------------------|-------------------|---------------------------------------------|
| QA / Broadcast Ops | K 102.7 FM        | Zero-error SLA, live system monitoring      |
| Clinical QA        | San Jose Hospital | Algorithm design, validation, documentation |
| Tech Support       | Charter Spectrum  | Jira/Zendesk, ticket management, 15% FCR ↑  |

---

> *I show up. I document everything. I don't break things.*
> Currently completing a Software Engineering degree at Hybridge · Certified in Git/GitHub & n8n automation.

---

**Jordi Yashua Contreras Blanch** · [paastor.blanch@gmail.com](mailto:paastor.blanch@gmail.com) · [github.com/JordiBlanch666](https://github.com/JordiBlanch666)

*Hybridge — Software Engineering · Second semester · 2025–2026*
