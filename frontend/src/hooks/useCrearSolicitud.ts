import { useState } from 'react'
import { crearSolicitudPublica, type SolicitudPublicaPayload, type SolicitudPublicaResponse } from '../services/solicitudes'
import { generateIdempotencyKey } from '../utils/idempotency'

export interface UseCrearSolicitudResult {
  crear: (payload: SolicitudPublicaPayload) => Promise<SolicitudPublicaResponse>
  isLoading: boolean
  error: unknown
  reset: () => void
  idempotencyKey: string
}

export function useCrearSolicitud(): UseCrearSolicitudResult {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<unknown>(null)
  const [idempotencyKey, setIdempotencyKey] = useState(() => generateIdempotencyKey())

  async function crear(payload: SolicitudPublicaPayload): Promise<SolicitudPublicaResponse> {
    setIsLoading(true)
    setError(null)
    try {
      const res = await crearSolicitudPublica(payload, { idempotencyKey })
      return res
    } catch (e) {
      setError(e)
      throw e
    } finally {
      setIsLoading(false)
    }
  }

  function reset() {
    setError(null)
    setIsLoading(false)
    setIdempotencyKey(generateIdempotencyKey())
  }

  return { crear, isLoading, error, reset, idempotencyKey }
}