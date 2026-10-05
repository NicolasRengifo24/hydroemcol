# Constitución de Hidroemcol

1. **Stack mínimo.** Solo lo ya instalado en `requirements.txt` y `package.json`; añadir
   dependencia exige explicar qué resuelve y pedir aprobación antes.
2. **La spec manda.** `CONTEXTO_MAESTRO.md` es la fuente del negocio y el código no la
   contradice; cambiar el modelo implica migración nueva y decisión anotada en `MEMORY.md`.
3. **El backend decide, la interfaz muestra.** Autorización, estados y cálculos se resuelven
   en Django; el frontend nunca aplica una regla por su cuenta ni la duplica.
4. **Tests sin dependencias nuevas.** Solo `manage.py test` con `django.test`. Cuando un
   cambio lo justifique, el agente lo propone y pregunta antes de escribirlo.
5. **Datos del cliente, solo los suyos.** Todo serializer público filtra por
   `visible_cliente=True`; jamás expone campos internos ni datos de otro servicio.
6. **Español en código y en pantalla.** Identificadores, comentarios y textos visibles en
   español; los mensajes del framework quedan en inglés (`LANGUAGE_CODE = 'en-us'`).
