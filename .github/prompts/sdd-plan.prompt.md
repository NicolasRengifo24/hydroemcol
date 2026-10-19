---
name: sdd-plan
description: Genera el plan técnico de una spec SDD aprobada, sin escribir código.
agent: planner
---

Spec: `specs/$1/`

Lee `docs/constitution.md`, `AGENTS.md`, `CONTEXTO_MAESTRO.md`, `MEMORY.md` y `spec.md`. Usa la skill `sdd`.

Si la spec no está aprobada o tiene dudas abiertas, detente y enuméralas. Si está lista, genera `plan.md` con archivos y responsabilidades, lógica pura, pseudocódigo, decisiones técnicas y alternativas descartadas, estrategia de verificación y RF cubiertos. No escribas código.
