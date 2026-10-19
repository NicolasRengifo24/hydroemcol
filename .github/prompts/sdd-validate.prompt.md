---
name: sdd-validate
description: Valida una implementación contra una spec SDD requisito por requisito, sin corregir archivos.
agent: reviewer
---

Valida `specs/$1/spec.md` contra la implementación actual.

Lee `plan.md`, `tasks.md`, `docs/constitution.md`, `AGENTS.md`, `CONTEXTO_MAESTRO.md` y el diff. Recorre cada RF, identifica tests y ejecuta las verificaciones disponibles. Para Django usa `python manage.py test`; para interfaz revisa responsive, accesibilidad y estados cuando sea posible.

No arregles nada. Entrega hallazgos primero y termina con `VEREDICTO: APROBADO` o `VEREDICTO: CAMBIOS NECESARIOS`.
