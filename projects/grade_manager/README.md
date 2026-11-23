# Grade Manager

A Python CLI to record and analyze student grades.

## Features

- Add students
- Record multiple grades per student
- View a report with the average and letter grade (A–F)
- Automatic JSON persistence

## How to run

```bash
python grade_manager.py
```

## Sample session

```
╔══════════════════════════════╗
║        Grade Manager         ║
╚══════════════════════════════╝

  [1] Add student
  [2] Record grade
  [3] View report
  [4] Exit

  Student              Grades   Average Letter
  ---------------------------------------------
  Ana García                3      88.3      B
  Carlos López              4      91.5      A
  María Martínez            2      74.0      C

  Class average: 84.6
```

## Concepts applied

| Concept            | Where it's used                               |
|--------------------|-----------------------------------------------|
| Functions          | `load_data`, `calculate_average`, etc.        |
| Data structures    | A dict stores students and their grades       |
| Loops              | Main menu loop and the report                 |
| Conditionals       | Input validation and letter-grade calculation |
| Files (JSON)       | Persistence with `json.load` / `json.dump`    |
| Error handling     | `try/except` when entering a grade            |
