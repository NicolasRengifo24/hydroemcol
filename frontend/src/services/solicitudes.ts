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
  empresa?: string
  correo_electronico: string
  telefono?: string
  whatsapp?: string
  descripcion_problema: string
  entregar_en_banco?: boolean
  avisar_para_coordinar?: boolean
  recoger?: boolean
  componentes: ComponenteSolicitud[]
  fotografias?: File[]
  idempotency_key?: string
  confirmar?: boolean
}

export interface SolicitudPublicaResponse {
  codigo: string
  enlace_seguimiento: string
}

type PayloadSinFotos = Omit<SolicitudPublicaPayload, 'fotografias' | 'idempotency_key'> & {
  idempotency_key: string
}

/**
 * Construye el `FormData` con el contrato multipart que espera el backend para
 * las solicitudes con fotografías (RF-5): las imágenes viajan bajo el campo
 * `fotografias` y los componentes con nombres indexados
 * (`componentes[0]tipo`, `componentes[0]cantidad`, …).
 */
export function construirFormDataSolicitud(
  payload: PayloadSinFotos,
  fotografias: File[],
): FormData {
  const fd = new FormData()

  fd.append('nombre_cliente', payload.nombre_cliente)
  if (payload.empresa) fd.append('empresa', payload.empresa)
  fd.append('correo_electronico', payload.correo_electronico)
  if (payload.telefono) fd.append('telefono', payload.telefono)
  if (payload.whatsapp) fd.append('whatsapp', payload.whatsapp)
  fd.append('descripcion_problema', payload.descripcion_problema)
  fd.append('entregar_en_banco', payload.entregar_en_banco ? 'true' : 'false')
  fd.append('avisar_para_coordinar', payload.avisar_para_coordinar ? 'true' : 'false')
  fd.append('recoger', payload.recoger ? 'true' : 'false')

  payload.componentes.forEach((componente, indice) => {
    fd.append(`componentes[${indice}]tipo`, componente.tipo)
    fd.append(`componentes[${indice}]cantidad`, String(componente.cantidad ?? 1))
    if (componente.marca) fd.append(`componentes[${indice}]marca`, componente.marca)
    if (componente.referencia) fd.append(`componentes[${indice}]referencia`, componente.referencia)
    if (componente.descripcion) fd.append(`componentes[${indice}]descripcion`, componente.descripcion)
  })

  fd.append('idempotency_key', payload.idempotency_key)
  fd.append('confirmar', payload.confirmar ? 'true' : 'false')

  fotografias.forEach((foto) => fd.append('fotografias', foto, foto.name))

  return fd
}

export async function crearSolicitudPublica(
  payload: SolicitudPublicaPayload,
  options?: { idempotencyKey?: string },
): Promise<SolicitudPublicaResponse> {
  const key = options?.idempotencyKey ?? payload.idempotency_key ?? generateIdempotencyKey()
  const { fotografias, ...resto } = payload
  const body: PayloadSinFotos = { ...resto, idempotency_key: key }

  if (fotografias && fotografias.length > 0) {
    return apiRequest<SolicitudPublicaResponse>('/api/solicitudes/', {
      method: 'POST',
      body: construirFormDataSolicitud(body, fotografias),
      idempotencyKey: key,
    })
  }

  return apiRequest<SolicitudPublicaResponse>('/api/solicitudes/', {
    method: 'POST',
    body: JSON.stringify(body),
    idempotencyKey: key,
  })
}