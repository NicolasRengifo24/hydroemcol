---
name: sdd-tasks
description: Divide un plan SDD aprobado en tareas pequeñas y verificables.
agent: planner
---

Spec: `specs/$1/`

A partir de `spec.md` y `plan.md`, genera `tasks.md` usando la skill `sdd`.

Crea tareas en orden de dependencia, de aproximadamente 20 a 30 minutos, con checkbox, RF cubiertos y una línea `Hecho cuando:` verificable. Intenta no superar diez tareas; si la spec es demasiado grande, indícalo en lugar de ocultar el problema.
