import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import type { ComponenteSeguimiento } from "../../services/api";
import {
  PASOS_PUBLICOS,
  comentarioPorPaso,
  nivelDePaso,
  type Paso,
} from "./pasosPublicos";

const transicionValvula = {
  duration: 0.35,
  ease: [0.22, 1, 0.36, 1],
} as const;

const transicionFlujo = {
  duration: 0.7,
  ease: [0.22, 1, 0.36, 1],
} as const;

export function CircuitoValvulas({
  paso,
  tipo,
  estado,
  historial,
}: {
  paso: string;
  tipo: string;
  estado: string;
  historial: ComponenteSeguimiento["historial"];
}) {
  const reducirMovimiento = useReducedMotion();
  const nivelActual = nivelDePaso(paso);
  const comentarios = comentarioPorPaso(historial);
  const [pasoAbierto, setPasoAbierto] = useState<Paso | null>(null);

  const progreso = PASOS_PUBLICOS.length > 1
    ? nivelActual / (PASOS_PUBLICOS.length - 1)
    : 1;

  return (
    <div className="seguimiento-circuito">
      <div className="seguimiento-circuito__medio">
        <div className="seguimiento-circuito__pista" aria-hidden="true">
          <div className="seguimiento-circuito__tuberia">
            <motion.span
              className="seguimiento-circuito__flujo"
              initial={reducirMovimiento ? false : { scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={reducirMovimiento ? { duration: 0 } : transicionFlujo}
            />
          </div>
          <motion.span
            className="seguimiento-circuito__pulso"
            initial={reducirMovimiento ? false : { scaleX: 0 }}
            animate={{ scaleX: progreso }}
            transition={reducirMovimiento ? { duration: 0 } : transicionFlujo}
          />
        </div>

        <ol className="seguimiento-circuito__pasos">
          {PASOS_PUBLICOS.map((nombre, indice) => {
            const activo = indice <= nivelActual;
            const actual = indice === nivelActual;
            const comentario = comentarios[nombre];
            const abierto = pasoAbierto === nombre;
            const detalleId = `detalle-${tipo}-${indice}`.replace(/\s+/g, "-");

            return (
              <li
                className={`seguimiento-circuito__nodo${
                  activo ? " is-active" : ""
                }${actual ? " is-current" : ""}`}
                key={nombre}
                style={{ "--nodo-index": indice } as React.CSSProperties}
              >
                <button
                  type="button"
                  className="seguimiento-circuito__nodo-boton"
                  aria-expanded={abierto}
                  aria-controls={detalleId}
                  aria-describedby={actual ? `${detalleId}-actual` : undefined}
                  onClick={() => setPasoAbierto(abierto ? null : nombre)}
                >
                  <motion.span
                    className="seguimiento-circuito__valvula"
                    aria-hidden="true"
                    initial={
                      reducirMovimiento ? false : { scale: 0.4, opacity: 0 }
                    }
                    animate={{
                      scale: activo ? (actual ? 1.08 : 1) : 0.75,
                      opacity: 1,
                      rotate: activo ? 90 : 0,
                    }}
                    transition={
                      reducirMovimiento
                        ? { duration: 0 }
                        : { ...transicionValvula, delay: indice * 0.12 }
                    }
                  />
                  <span className="seguimiento-circuito__etiqueta">
                    {nombre}
                  </span>
                </button>

                <AnimatePresence initial={false}>
                  {abierto && (
                    <motion.div
                      id={detalleId}
                      className="seguimiento-circuito__detalle"
                      initial={
                        reducirMovimiento ? false : { opacity: 0, height: 0 }
                      }
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={
                        reducirMovimiento ? { duration: 0 } : { duration: 0.25 }
                      }
                    >
                      {comentario ? (
                        <>
                          <p className="seguimiento-circuito__detalle-estado">
                            {comentario.estado}
                          </p>
                          <p>{comentario.comentario}</p>
                          <time dateTime={comentario.fecha}>
                            {new Intl.DateTimeFormat("es-CO", {
                              dateStyle: "medium",
                            }).format(new Date(comentario.fecha))}
                          </time>
                        </>
                      ) : (
                        <p className="seguimiento-circuito__detalle-vacio">
                          Sin comentario del equipo para este paso.
                        </p>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </li>
            );
          })}
        </ol>
      </div>

      <p
        className="seguimiento-circuito__actual"
        id={`detalle-${tipo}-${nivelActual}-actual`.replace(/\s+/g, "-")}
      >
        <span className="seguimiento-circuito__actual-etiqueta">
          Estado actual
        </span>
        {estado}
      </p>
    </div>
  );
}
