import { useEffect, useState } from 'react'

/**
 * Devuelve `true` cuando una operación lleva activa más de `esperaMs`.
 * Sirve para avisar que el servicio puede tardar en iniciar (cold start).
 */
export function useEsperaProlongada(activo: boolean, esperaMs = 8000): boolean {
  const [prolongada, setProlongada] = useState(false)

  useEffect(() => {
    if (!activo) return

    const temporizador = window.setTimeout(() => setProlongada(true), esperaMs)
    return () => {
      window.clearTimeout(temporizador)
      setProlongada(false)
    }
  }, [activo, esperaMs])

  return activo && prolongada
}
