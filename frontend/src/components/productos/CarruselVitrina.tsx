import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ImagenVitrina } from '../../services/vitrina'

const INTERVALO_AUTOPLAY_MS = 6000

interface CarruselVitrinaProps {
  imagenes: ImagenVitrina[]
}

// Carrusel solo visual (RF-VIT-19/20): no tiene enlace, clic, botón, CTA ni
// WhatsApp sobre la imagen. Con 0 imágenes no renderiza; con 1 es estático; con
// 2+ avanza automáticamente con transición suave y se detiene cuando la pestaña
// queda oculta o el usuario pide menos movimiento.
export function CarruselVitrina({ imagenes }: CarruselVitrinaProps) {
  const [indice, setIndice] = useState(0)
  const [documentoOculto, setDocumentoOculto] = useState(
    () => typeof document !== 'undefined' && document.visibilityState === 'hidden',
  )
  const [reducirMovimiento, setReducirMovimiento] = useState(false)
  const [fallidas, setFallidas] = useState<Set<number>>(() => new Set())

  useEffect(() => {
    const consulta = window.matchMedia('(prefers-reduced-motion: reduce)')
    const actualizar = () => setReducirMovimiento(consulta.matches)
    actualizar()
    consulta.addEventListener('change', actualizar)
    return () => consulta.removeEventListener('change', actualizar)
  }, [])

  useEffect(() => {
    const alCambiarVisibilidad = () => {
      setDocumentoOculto(document.visibilityState === 'hidden')
    }
    document.addEventListener('visibilitychange', alCambiarVisibilidad)
    return () => document.removeEventListener('visibilitychange', alCambiarVisibilidad)
  }, [])

  const disponibles = useMemo(
    () => imagenes.map((_, posicion) => posicion).filter((posicion) => !fallidas.has(posicion)),
    [imagenes, fallidas],
  )

  const indiceActual = disponibles.includes(indice) ? indice : disponibles[0]

  const mover = useCallback(
    (paso: number) => {
      if (disponibles.length === 0) return
      const posicionActual = disponibles.indexOf(indiceActual)
      const base = posicionActual === -1 ? 0 : posicionActual
      setIndice(disponibles[(base + paso + disponibles.length) % disponibles.length])
    },
    [disponibles, indiceActual],
  )

  useEffect(() => {
    if (disponibles.length < 2 || documentoOculto || reducirMovimiento) return
    const temporizador = window.setInterval(() => mover(1), INTERVALO_AUTOPLAY_MS)
    return () => window.clearInterval(temporizador)
  }, [disponibles.length, documentoOculto, mover, reducirMovimiento])

  if (imagenes.length === 0 || disponibles.length === 0) return null

  const descartarImagen = (posicion: number) => {
    setFallidas((previas) => {
      const siguientes = new Set(previas)
      siguientes.add(posicion)
      return siguientes
    })
  }

  return (
    <div
      className={`carrusel-vitrina${imagenes.length === 1 ? ' carrusel-vitrina--unica' : ''}`}
      role="region"
      aria-roledescription="carrusel"
      aria-label="Imágenes de productos"
    >
      <div className="carrusel-vitrina__marco">
        {imagenes.map((imagen, posicion) => (
          <div
            key={posicion}
            className={`carrusel-vitrina__diapositiva${posicion === indiceActual ? ' carrusel-vitrina__diapositiva--activa' : ''}`}
            aria-hidden={posicion !== indiceActual}
          >
            <img
              className="carrusel-vitrina__imagen"
              src={imagen.url}
              alt={posicion === indiceActual ? imagen.alt : ''}
              loading={posicion === 0 ? 'eager' : 'lazy'}
              decoding="async"
              onError={() => descartarImagen(posicion)}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
