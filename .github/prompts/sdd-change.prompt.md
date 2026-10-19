---
name: sdd-change
description: Actualiza una spec SDD existente con un nuevo requisito, sin tocar código.
agent: planner
---

Spec: `specs/$1/`
Cambio solicitado:

$ARGUMENTS

Lee la spec, `docs/constitution.md`, `AGENTS.md`, `CONTEXTO_MAESTRO.md` y usa la skill `sdd`.

Actualiza únicamente `spec.md` con el nuevo RF o el cambio en EARS, casos límite y fuera de alcance. Indica qué partes de `plan.md` y `tasks.md` deberán actualizarse. No modifiques código ni esos dos archivos. Muestra el diff y espera aprobación.
