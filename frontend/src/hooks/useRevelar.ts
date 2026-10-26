import { useReducedMotion, type MotionProps } from 'framer-motion'

type Direccion = 'arriba' | 'abajo' | 'izquierda' | 'derecha' | 'escala'

interface OpcionesRevelar {
  direccion?: Direccion
  retraso?: number
  duracion?: number
  distancia?: number
  escala?: number
  cantidad?: number
  margen?: string
  unaVez?: boolean
}

const CURVA: [number, number, number, number] = [0.22, 0.61, 0.36, 1]

/**
 * Devuelve las propiedades de Framer Motion para revelar un bloque al entrar
 * en el viewport. Solo anima opacidad y transformaciones, y se desactiva por
 * completo con `prefers-reduced-motion`.
 */
export function useRevelar({
  direccion = 'arriba',
  retraso = 0,
  duracion = 0.55,
  distancia = 16,
  escala = 0.995,
  cantidad = 0.16,
  margen = '0px 0px -8% 0px',
  unaVez = true,
}: OpcionesRevelar = {}): MotionProps {
  const reducirMovimiento = useReducedMotion()

  if (reducirMovimiento) {
    return { initial: false }
  }

  const desde = {
    arriba: { x: 0, y: distancia },
    abajo: { x: 0, y: -distancia },
    izquierda: { x: -distancia, y: 0 },
    derecha: { x: distancia, y: 0 },
    escala: { x: 0, y: distancia * 0.5 },
  }[direccion]

  return {
    initial: {
      opacity: 0,
      ...desde,
      scale: direccion === 'escala' ? 0.97 : escala,
    },
    whileInView: { opacity: 1, x: 0, y: 0, scale: 1 },
    viewport: { once: unaVez, amount: cantidad, margin: margen },
    transition: { duration: duracion, delay: retraso, ease: CURVA },
  }
}
