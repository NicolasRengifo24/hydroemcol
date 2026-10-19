---
name: sdd-spec
description: Entrevista y redacta una spec SDD para una nueva funcionalidad de Hidroemcol.
agent: planner
---

Nueva spec: `specs/$1/`
Idea inicial:

$ARGUMENTS

No escribas código. Lee `docs/constitution.md`, `AGENTS.md`, `CONTEXTO_MAESTRO.md`, `MEMORY.md` y usa la skill `sdd`.

Haz preguntas de una en una para eliminar ambigüedades, con un máximo de cinco. Cuando las decisiones estén claras, genera `spec.md` con requisitos EARS, casos límite, fuera de alcance y estado `borrador`. Incluye solo qué y por qué, no stack, arquitectura ni archivos.
