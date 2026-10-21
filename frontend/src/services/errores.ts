// Traduce la respuesta de error del backend a un texto para el usuario.
// Django REST Framework responde con `detail` (errores de acción), con una lista
// de mensajes (errores no ligados a un campo) o con un diccionario campo → mensajes.

function mensajeDeRespuesta(data: unknown): string | undefined {
  if (typeof data === 'string') return data || undefined
  if (Array.isArray(data)) return data.map(mensajeDeRespuesta).find((texto) => texto)
  if (typeof data === 'object' && data !== null) {
    const detail = (data as { detail?: unknown }).detail
    if (typeof detail === 'string' && detail) return detail
    return Object.values(data).map(mensajeDeRespuesta).find((texto) => texto)
  }
  return undefined
}

export function mensajeDeError(error: unknown, mensajeGenerico: string): string {
  if (typeof error === 'object' && error !== null && 'data' in error) {
    const texto = mensajeDeRespuesta((error as { data?: unknown }).data)
    if (texto) return texto
  }
  return mensajeGenerico
}
