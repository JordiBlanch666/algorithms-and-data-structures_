# Programación Orientada a Objetos

Segundo cuatrimestre — Ingeniería en Software · Hybridge

## Los cuatro pilares

| # | Archivo | Concepto | Demo |
|---|---------|----------|------|
| 1 | `01_clases_objetos.py` | Clases y objetos | Catálogo de productos con IVA |
| 2 | `02_encapsulacion.py` | Encapsulación | Cuenta bancaria con atributos privados |
| 3 | `03_herencia.py` | Herencia + `super()` | Jerarquía Animal → Perro / Gato / Loro |
| 4 | `04_polimorfismo.py` | Polimorfismo + ABC | Figuras geométricas con interfaz común |

## Proyecto integrador: Sistema Bancario (`herencia.py`)

Aplica los cuatro pilares en un solo módulo coherente:

```
Cuenta (ABC)               ← clase abstracta, encapsulación
├── CuentaAhorro           ← herencia, aplica interés
└── CuentaCorriente        ← herencia, límite de sobregiro
```

**Conceptos aplicados:**

| Concepto | Dónde |
|----------|-------|
| Encapsulación | `__saldo` solo modificable via `depositar` / `retirar` |
| Herencia | `CuentaAhorro` y `CuentaCorriente` extienden `Cuenta` |
| Polimorfismo | `retirar()` se comporta distinto en cada subclase |
| Abstracción | `Cuenta` es abstracta; no se puede instanciar directamente |
| `super()` | El constructor hijo llama al padre con `super().__init__()` |
| Properties | `@property` expone saldo de solo lectura |

```bash
python poo/herencia.py
python poo/04_polimorfismo.py
```
