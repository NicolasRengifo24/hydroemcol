---
name: sdd-status
description: Consulta el estado actual de una spec SDD y determina el siguiente paso.
agent: planner
---

Spec: `specs/$1/`

Lee los archivos existentes de la spec y `MEMORY.md`. Indica brevemente:

1. Fase y estado actual.
2. Tareas completadas y pendientes.
3. Siguiente paso exacto y prompt `/sdd-*` recomendado.

No modifiques archivos.
