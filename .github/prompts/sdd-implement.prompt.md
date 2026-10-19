---
name: sdd-implement
description: Implementa una única tarea aprobada de una spec SDD de Hidroemcol.
agent: implementer
---

Implementa únicamente la tarea `$2` de `specs/$1/tasks.md`.

Lee `spec.md`, `plan.md`, `tasks.md`, `docs/constitution.md`, `AGENTS.md`, `CONTEXTO_MAESTRO.md` y `MEMORY.md`. No rediseñes el plan ni empieces otra tarea.

Escribe primero los tests si la tarea y las reglas del proyecto los requieren. Para backend verifica con `python manage.py test`; para frontend verifica TypeScript, imports, rutas y comportamiento visual cuando sea posible. Marca la tarea como hecha solo si está completa y resume RF, archivos, verificaciones y decisiones pendientes.
