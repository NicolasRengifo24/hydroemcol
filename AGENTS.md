# Instrucciones del proyecto — Hidroemcol

## 1. Contexto principal

Antes de realizar cambios importantes en el proyecto, leer y respetar:

`contexto-proyecto.md`

Este archivo contiene el contexto maestro del proyecto Hidroemcol, incluyendo:

- objetivo del sistema;
- modelo de negocio;
- arquitectura;
- tecnologías;
- entidades y relaciones;
- flujos funcionales;
- decisiones previamente tomadas;
- alcance del proyecto.

No inventar información que contradiga el contexto maestro.

---

## 2. Arquitectura

El proyecto está dividido en:

- `frontend/` → aplicación React.
- `backend/` → API y lógica del servidor.

Respetar la separación entre frontend y backend.

No cambiar la arquitectura general del proyecto sin consultar primero al usuario.

---

## 3. Regla principal de decisiones

El agente actúa como asistente de desarrollo.

Puede:

- analizar;
- proponer;
- explicar;
- implementar cambios solicitados;
- detectar problemas;
- sugerir mejoras.

Pero debe preguntar antes de realizar cambios que alteren decisiones importantes del proyecto.

Esto incluye especialmente:

- cambiar la arquitectura;
- modificar el modelo de base de datos;
- eliminar o renombrar entidades;
- cambiar relaciones entre entidades;
- cambiar contratos de API;
- crear endpoints que modifiquen el diseño establecido;
- cambiar tecnologías principales;
- instalar dependencias importantes;
- introducir una nueva librería que pueda reemplazar una solución existente.

---

## 4. No inventar requisitos

Si una funcionalidad, regla de negocio, dato o comportamiento no está definido:

1. identificar qué información falta;
2. explicar brevemente las opciones relevantes;
3. preguntar al usuario antes de asumir una decisión importante.

No inventar requisitos de negocio para completar una implementación.

---

## 5. Frontend

El frontend utiliza React + TypeScript.

Las interfaces deben priorizar:

- UX clara;
- responsive design;
- accesibilidad;
- componentes reutilizables;
- consistencia visual;
- jerarquía visual;
- estados de carga;
- estados vacíos;
- estados de error;
- feedback claro al usuario.

La interfaz debe funcionar correctamente en:

- móvil;
- tablet;
- escritorio.

No diseñar únicamente para escritorio y adaptar posteriormente.

---

## 6. Diseño de Hidroemcol

La interfaz debe representar una empresa técnica e industrial especializada en:

- sistemas hidráulicos;
- sistemas electrohidráulicos;
- repuestos;
- importación sobre pedido;
- servicios técnicos;
- diagnóstico;
- reparación;
- banco de pruebas;
- soluciones de control.

El diseño debe transmitir principalmente:

- confianza;
- precisión técnica;
- profesionalismo;
- capacidad industrial;
- claridad;
- facilidad de contacto.

Evitar interfaces genéricas que parezcan una plantilla de una empresa tecnológica sin relación con el sector industrial.

---

## 7. Antes de modificar código existente

Antes de modificar un archivo:

1. leer el archivo;
2. entender su responsabilidad;
3. revisar cómo se relaciona con otros archivos;
4. reutilizar las soluciones existentes cuando sea posible.

No reemplazar código simplemente porque existe una alternativa diferente.

---

## 8. Cambios pequeños y verificables

Preferir cambios pequeños y coherentes.

Después de realizar cambios:

- verificar errores de TypeScript;
- verificar imports;
- verificar rutas;
- ejecutar las pruebas disponibles cuando corresponda;
- comprobar visualmente los cambios de frontend cuando sea posible.

---

## 9. Comunicación

Cuando una tarea tenga varias decisiones posibles:

- explicar brevemente las alternativas;
- recomendar una implementación técnica solo cuando esté justificada;
- pedir confirmación cuando la decisión afecte arquitectura, datos o alcance.

No ocultar decisiones importantes dentro de una implementación.

---

## 10. Skills de diseño

Cuando una tarea implique diseño o modificación importante del frontend, utilizar las skills de diseño disponibles en `.opencode/skills/`.

Las skills complementan estas instrucciones y no sustituyen el contexto maestro del proyecto.

Si existe conflicto entre una skill genérica y una decisión específica documentada para Hidroemcol, prevalece la decisión específica del proyecto.

## 11 verificacion

no hay test automaticos . despues de cada cambio verifica con el mcp ......

## 12 reglas

lee el archivo docs/constitution.md antes de tocar el codigo
