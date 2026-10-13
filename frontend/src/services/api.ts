export interface RequestOptions extends RequestInit {
  idempotencyKey?: string
}

export type EstadoSesion = 'anonima' | 'autenticando' | 'autenticada'

export interface CredencialesInicio {
  username: string
  password: string
}

type ErrorApi = Error & { status: number; data: unknown }
type OyenteSesion = (estado: EstadoSesion) => void
type RequestOptionsInternas = RequestOptions & { _reintentoSesion?: boolean }

const baseApi = import.meta.env.VITE_API_URL ?? ''
const rutasConCsrf = new Set(['/api/login/', '/api/refresh/', '/api/logout/'])
const rutasSinRenovacion = new Set([
  '/api/login/',
  '/api/refresh/',
  '/api/logout/',
  '/api/csrf/',
])

let accessToken: string | null = null
let estadoSesion: EstadoSesion = 'anonima'
let refreshEnCurso: Promise<string | null> | null = null
const oyentesSesion = new Set<OyenteSesion>()

function cambiarEstadoSesion(nuevoEstado: EstadoSesion): void {
  estadoSesion = nuevoEstado
  oyentesSesion.forEach((oyente) => oyente(estadoSesion))
}

function rutaDe(endpoint: string): string {
  try {
    return new URL(endpoint, window.location.origin).pathname
  } catch {
    return endpoint.split('?')[0]
  }
}

function urlApi(endpoint: string): string {
  if (/^https?:\/\//i.test(endpoint)) return endpoint
  return `${baseApi}${endpoint}`
}

function leerCsrfDeCookie(): string | null {
  if (typeof document === 'undefined') return null
  const cookie = document.cookie
    .split('; ')
    .find((parte) => parte.startsWith('csrftoken='))
  if (!cookie) return null

  const valor = cookie.slice('csrftoken='.length)
  try {
    return decodeURIComponent(valor)
  } catch {
    return valor
  }
}

function esErrorApi(error: unknown): error is ErrorApi {
  return error instanceof Error && typeof (error as Partial<ErrorApi>).status === 'number'
}

function limpiarSesion(): void {
  accessToken = null
  cambiarEstadoSesion('anonima')
}

function dirigirAlLogin(): void {
  if (typeof window === 'undefined') return
  if (window.location.pathname !== '/admin/login') {
    window.location.assign('/admin/login')
  }
}

export function obtenerEstadoSesion(): EstadoSesion {
  return estadoSesion
}

export function suscribirseSesion(oyente: OyenteSesion): () => void {
  oyentesSesion.add(oyente)
  return () => oyentesSesion.delete(oyente)
}

/** Solicita una cookie CSRF y devuelve el valor que debe viajar en el encabezado. */
export async function obtenerCsrf(): Promise<string> {
  await apiRequest('/api/csrf/', { method: 'GET' })
  const csrf = leerCsrfDeCookie()
  if (!csrf) throw new Error('No se pudo obtener el token CSRF')
  return csrf
}

export async function iniciarSesion(credenciales: CredencialesInicio): Promise<void> {
  cambiarEstadoSesion('autenticando')
  try {
    const respuesta = await apiRequest<{ access: string }>('/api/login/', {
      method: 'POST',
      body: JSON.stringify(credenciales),
    })
    accessToken = respuesta.access
    cambiarEstadoSesion('autenticada')
  } catch (error) {
    limpiarSesion()
    throw error
  }
}

async function renovarSesion(): Promise<string | null> {
  try {
    const respuesta = await apiRequest<{ access: string }>('/api/refresh/', {
      method: 'POST',
    })
    accessToken = respuesta.access
    cambiarEstadoSesion('autenticada')
    return accessToken
  } catch (error) {
    if (esErrorApi(error) && error.status === 401) {
      limpiarSesion()
      dirigirAlLogin()
      return null
    }
    throw error
  }
}

/** Coordina todos los refresh para que solo haya una renovación simultánea. */
export function refrescarSesion(): Promise<string | null> {
  if (!refreshEnCurso) {
    refreshEnCurso = renovarSesion().finally(() => {
      refreshEnCurso = null
    })
  }
  return refreshEnCurso
}

export async function cerrarSesion(): Promise<void> {
  try {
    await apiRequest('/api/logout/', { method: 'POST' })
  } finally {
    limpiarSesion()
  }
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestOptionsInternas = {},
): Promise<T> {
  const {
    idempotencyKey,
    headers: customHeaders,
    _reintentoSesion: esReintento,
    ...rest
  } = options
  const headers = new Headers(customHeaders)
  const ruta = rutaDe(endpoint)

  if (accessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${accessToken}`)
  }

  if (rutasConCsrf.has(ruta) && !headers.has('X-CSRFToken')) {
    headers.set('X-CSRFToken', await obtenerCsrf())
  }

  if (!headers.has('Content-Type') && rest.body && !(rest.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  if (idempotencyKey && !headers.has('Idempotency-Key')) {
    headers.set('Idempotency-Key', idempotencyKey)
  }

  const res = await fetch(urlApi(endpoint), {
    ...rest,
    credentials: 'include',
    headers,
  })

  if (!res.ok) {
    let data: unknown
    try {
      data = await res.json()
    } catch {
      data = { detail: await res.text() }
    }
    const error = new Error('API error') as ErrorApi
    error.status = res.status
    error.data = data

    if (res.status === 401 && !rutasSinRenovacion.has(ruta) && !esReintento) {
      const nuevoAccess = await refrescarSesion()
      if (nuevoAccess) {
        return apiRequest<T>(endpoint, { ...options, _reintentoSesion: true })
      }
    }
    throw error
  }

  if (res.status === 204) return {} as T

  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) return (await res.json()) as T
  return (await res.text()) as unknown as T
}
