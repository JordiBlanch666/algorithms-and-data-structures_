# Gestor de Calificaciones

CLI en Python para registrar y analizar calificaciones de alumnos.

## Funcionalidades

- Agregar alumnos
- Registrar múltiples calificaciones por alumno
- Ver reporte con promedio y letra (A–F)
- Persistencia automática en JSON

## Cómo ejecutar

```bash
python gestor.py
```

## Ejemplo de uso

```
╔══════════════════════════════╗
║   Gestor de Calificaciones   ║
╚══════════════════════════════╝

  [1] Agregar alumno
  [2] Registrar calificación
  [3] Ver reporte
  [4] Salir

  Alumno             Califs  Promedio  Letra
  ---------------------------------------------
  Ana García              3      88.3      B
  Carlos López            4      91.5      A
  María Martínez          2      74.0      C

  Promedio del grupo: 84.6
```

## Conceptos aplicados

| Concepto           | Dónde se usa                              |
|--------------------|-------------------------------------------|
| Funciones          | `cargar_datos`, `calcular_promedio`, etc. |
| Estructuras (dict) | Almacenamiento de alumnos y calificaciones |
| Bucles             | Ciclo principal del menú, reporte         |
| Condicionales      | Validaciones, cálculo de letra            |
| Archivos (JSON)    | Persistencia con `json.load / json.dump`  |
| Manejo de errores  | `try/except` en entrada de calificación   |
