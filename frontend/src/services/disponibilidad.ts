export type EstadoDisponibilidad = 'desconocido' | 'disponible' | 'no_disponible'

export interface FotoDisponibilidad {
  estado: EstadoDisponibilidad
  ultimaComprobacion: number | null
}

type OyenteDisponibilidad = () => void

const baseApi = import.meta.env.VITE_API_URL ?? ''
const oyentes = new Set<OyenteDisponibilidad>()

let foto: FotoDisponibilidad = {
  estado: 'desconocido',
  ultimaComprobacion: null,
}

let sondeoEnCurso: Promise<boolean> | null = null

function publicar(siguiente: Partial<FotoDisponibilidad>): void {
  const actualizada: FotoDisponibilidad = { ...foto, ...siguiente }
  if (
    actualizada.estado === foto.estado &&
    actualizada.ultimaComprobacion === foto.ultimaComprobacion
  ) {
    return
  }
  foto = actualizada
  oyentes.forEach((oyente) => oyente())
}

export function obtenerFotoDisponibilidad(): FotoDisponibilidad {
  return foto
}

export function suscribirseDisponibilidad(oyente: OyenteDisponibilidad): () => void {
  oyentes.add(oyente)
  return () => {
    oyentes.delete(oyente)
  }
}

/** Marca la API como disponible. No notifica si ya lo estaba. */
export function marcarDisponible(): void {
  if (foto.estado === 'disponible') return
  publicar({ estado: 'disponible', ultimaComprobacion: Date.now() })
}

/** Marca la API como fuera de línea y actualiza la hora de la última comprobación. */
export function marcarNoDisponible(): void {
  publicar({ estado: 'no_disponible', ultimaComprobacion: Date.now() })
}

/**
 * Indica si un error debe interpretarse como caída de infraestructura.
 *
 * Los errores de validación, autenticación, permisos o conflicto (4xx) nunca
 * activan el modo mantenimiento. Los errores de red y las respuestas 5xx que
 * no son JSON sí. `api.ts` marca explícitamente los casos dudosos con la
 * propiedad `infraestructura`.
 */
export function esFalloDeInfraestructura(error: unknown): boolean {
  if (error instanceof TypeError) return true
  if (typeof error === 'object' && error !== null && 'infraestructura' in error) {
    return (error as { infraestructura?: unknown }).infraestructura === true
  }
  return false
}

function urlHealthz(): string {
  if (/^https?:\/\//i.test(baseApi)) {
    return `${baseApi.replace(/\/$/, '')}/healthz/`
  }
  // En desarrollo sin VITE_API_URL se usa el proxy de Vite.
  return '/healthz/'
}

async function ejecutarSondeo(tiempoMaximoMs: number): Promise<boolean> {
  const controlador = new AbortController()
  const temporizador = window.setTimeout(() => controlador.abort(), tiempoMaximoMs)

  try {
    const res = await fetch(`${urlHealthz()}?t=${Date.now()}`, {
      method: 'GET',
      cache: 'no-store',
      credentials: 'omit',
      signal: controlador.signal,
    })
    const tipoContenido = res.headers.get('content-type') ?? ''
    const esJson = tipoContenido.includes('application/json')

    if (res.ok && esJson) {
      const datos: unknown = await res.json().catch(() => null)
      if (
        datos &&
        typeof datos === 'object' &&
        (datos as { status?: unknown }).status === 'ok'
      ) {
        marcarDisponible()
        return true
      }
    }

    marcarNoDisponible()
    return false
  } catch {
    marcarNoDisponible()
    return false
  } finally {
    window.clearTimeout(temporizador)
  }
}

/**
 * Comprueba el endpoint de salud `/healthz/` sin lanzar peticiones en paralelo.
 * Devuelve `true` cuando la API responde correctamente.
 */
export function comprobarApi(tiempoMaximoMs = 8000): Promise<boolean> {
  if (!sondeoEnCurso) {
    sondeoEnCurso = ejecutarSondeo(tiempoMaximoMs).finally(() => {
      sondeoEnCurso = null
    })
  }
  return sondeoEnCurso
}
