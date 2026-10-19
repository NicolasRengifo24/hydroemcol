---
name: sdd-clarify
description: Revisa una spec SDD de Hidroemcol como QA y detecta problemas sin resolverlos.
agent: reviewer
---

Revisa `specs/$1/spec.md` como QA profesional.

Lee `docs/constitution.md`, `AGENTS.md`, `CONTEXTO_MAESTRO.md` y usa la skill `sdd`.

Lista únicamente:

1. Ambigüedades que impiden verificar requisitos.
2. Contradicciones entre requisitos.
3. Casos límite no cubiertos.
4. Conflictos con la constitución.

No propongas soluciones todavía y no modifiques archivos.
