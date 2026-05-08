# Object-Oriented Programming

Second semester — Software Engineering · Hybridge

## The four pillars

| # | File | Concept | Demo |
|---|------|---------|------|
| 1 | `01_clases_objetos.py` | Classes & objects | Product catalog with VAT |
| 2 | `02_encapsulacion.py` | Encapsulation | Bank account with private attributes |
| 3 | `03_herencia.py` | Inheritance + `super()` | Animal → Dog / Cat / Parrot hierarchy |
| 4 | `04_polimorfismo.py` | Polymorphism + ABC | Geometric shapes with a common interface |

## Integrating project: Banking System (`herencia.py`)

Applies all four pillars in one cohesive module:

```
Account (ABC)              ← abstract class, encapsulation
├── SavingsAccount         ← inheritance, applies interest
└── CheckingAccount        ← inheritance, overdraft limit
```

**Concepts applied:**

| Concept | Where |
|---------|-------|
| Encapsulation | `__balance` only modified via `deposit` / `withdraw` |
| Inheritance | `SavingsAccount` and `CheckingAccount` extend `Account` |
| Polymorphism | `withdraw()` behaves differently in each subclass |
| Abstraction | `Account` is abstract — cannot be instantiated directly |
| `super()` | Child constructor delegates initialization to parent |
| `@property` | Read-only balance exposed cleanly without a getter method |

```bash
python poo/herencia.py
python poo/04_polimorfismo.py
```
