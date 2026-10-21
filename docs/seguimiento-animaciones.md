# Animaciones del seguimiento

La vista pública de seguimiento usa `framer-motion` para representar el avance de cada componente con un circuito hidráulico 2D compuesto por tubería, flujo y válvulas.

## Variantes de estado

`CircuitoValvulas` convierte la fase pública del componente en cuatro niveles:

- `recibido`: primera válvula activa.
- `revision`: segunda válvula abierta.
- `pruebas`: tercera válvula abierta.
- `finalizado`: circuito completo y última válvula activa.

La información de negocio sigue llegando desde el backend. La animación solo representa `paso_publico` y no calcula ni modifica estados.

## Transiciones

- Cambio completo de estado: `duration: 0.5`, con easing `[0.22, 1, 0.36, 1]`.
- Flujo continuo: `opacity` se anima durante `2.2s` para sugerir presión circulando por la tubería.
- Apertura de válvula: transición de `0.25s` para feedback inmediato.
- Cambio completo de estado: transición de `0.5s` con easing `[0.22, 1, 0.36, 1]`.
- `useReducedMotion()` desactiva los pulsos y deja las válvulas en su posición final.

## Ejemplo

```tsx
const pasos = ["Recibido", "Revisión y cotización", "Pruebas", "Finalizado"];

const variantes = {
  recibido: 0,
  revision: 1,
  pruebas: 2,
  finalizado: 3,
};

function CircuitoValvulas({ nivel }: { nivel: keyof typeof variantes }) {
  const reducirMovimiento = useReducedMotion();
  const nivelActual = variantes[nivel];

  return (
    <motion.div
      className="seguimiento-circuito"
      aria-label={`Fase ${pasos[nivelActual]}`}
    >
      {pasos.map((paso, indice) => (
        <motion.span
          key={paso}
          className={
            indice <= nivelActual
              ? "seguimiento-circuito__valvula is-active"
              : "seguimiento-circuito__valvula"
          }
          animate={{ rotate: indice <= nivelActual ? 90 : 0 }}
          transition={
            reducirMovimiento
              ? { duration: 0 }
              : {
                  duration: indice === nivelActual ? 0.5 : 0.25,
                  ease: "easeOut",
                }
          }
        />
      ))}
    </motion.div>
  );
}
```

Las animaciones son decorativas y no reemplazan el texto visible del estado ni la lista accesible de fases.
