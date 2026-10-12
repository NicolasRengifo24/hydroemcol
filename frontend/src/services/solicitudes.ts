import { apiRequest } from './api'
import { generateIdempotencyKey } from '../utils/idempotency'

export interface ComponenteSolicitud {
  tipo: string
  marca?: string
  referencia?: string
  descripcion?: string
  cantidad?: number
}

export interface SolicitudPublicaPayload {
  nombre_cliente: string
  correo_electronico: string
  telefono: string
  tipo_servicio: string
  descripcion_problema: string
  componentes: ComponenteSolicitud[]
  idempotency_key?: string
}

export interface SolicitudPublicaResponse {
  codigo: string
  enlace_seguimiento: string
}

export async function crearSolicitudPublica(
  payload: SolicitudPublicaPayload,
  options?: { idempotencyKey?: string },
): Promise<SolicitudPublicaResponse> {
  const key = options?.idempotencyKey ?? payload.idempotency_key ?? generateIdempotencyKey()
  const body = { ...payload, idempotency_key: key }

  return apiRequest<SolicitudPublicaResponse>('/api/solicitudes/', {
    method: 'POST',
    body: JSON.stringify(body),
    idempotencyKey: key,
  })
}