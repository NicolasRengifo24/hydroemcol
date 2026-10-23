export interface RequestOptions extends RequestInit {
  idempotencyKey?: string
}

export type EstadoSesion = 'anonima' | 'autenticando' | 'autenticada'

export interface CredencialesInicio {
  username: string
  password: string
}

export type ErrorApi = Error & {
  status: number
  data: unknown
  requiereRecarga?: boolean
}
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

// Mensaje para respuestas del servidor que no son JSON (p. ej. la página de
// error de Django). El contenido original no se muestra al usuario.
const MENSAJE_SERVIDOR_NO_DISPONIBLE =
  'El servidor no pudo completar la operación. Inténtalo de nuevo en unos minutos.'

function limpiarSesion(): void {
  accessToken = null
  cambiarEstadoSesion('anonima')
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
  const respuesta = await apiRequest<{ csrfToken?: string }>('/api/csrf/', { method: 'GET' })
  const csrf = (respuesta && typeof respuesta === 'object' && 'csrfToken' in respuesta && typeof respuesta.csrfToken === 'string')
    ? respuesta.csrfToken
    : leerCsrfDeCookie()
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
      // El refresh cookie dejó de ser válido (caducó o rotó en otra pestaña).
      // La redirección la resuelve quien observa la sesión (el guard), para
      // conservar el destino original (RF-EST-14/15).
      limpiarSesion()
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

let bootstrapEnCurso: Promise<EstadoSesion> | null = null

async function ejecutarBootstrap(): Promise<EstadoSesion> {
  cambiarEstadoSesion('autenticando')
  try {
    // Reutiliza el single-flight de `refrescarSesion()` (D-9). Un `null` es un
    // 401 (cookie inválida o rotada en otra pestaña): se reintenta una sola vez.
    let token = await refrescarSesion()
    if (!token) {
      token = await refrescarSesion()
    }
    if (token) return 'autenticada'

    limpiarSesion()
    return 'anonima'
  } catch {
    // Error de red, 5xx o 429: no se reintenta y la sesión queda anónima.
    limpiarSesion()
    return 'anonima'
  }
}

/**
 * Restaura la sesión al cargar una ruta administrativa (RF-EST-14/15).
 *
 * Si ya hay sesión, no hace nada. Si no, pide un refresh reutilizando el
 * single-flight; reintenta una vez ante 401 y termina en `'autenticada'` o en
 * `'anonima'`. No persiste tokens: el `access` vive solo en memoria.
 */
export function bootstrapSesion(): Promise<EstadoSesion> {
  if (estadoSesion === 'autenticada') return Promise.resolve('autenticada')
  if (!bootstrapEnCurso) {
    bootstrapEnCurso = ejecutarBootstrap().finally(() => {
      bootstrapEnCurso = null
    })
  }
  return bootstrapEnCurso
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
    // El cuerpo se lee una sola vez: leerlo primero como JSON y caer a `text()`
    // lanzaba "body stream already read" cuando la respuesta de error no era
    // JSON (p. ej. el 401 de /api/refresh/), enmascarando el error HTTP y
    // rompiendo la detección de sesión (RF-EST-14/15).
    const texto = await res.text()
    try {
      data = texto ? JSON.parse(texto) : {}
    } catch {
      // El servidor devolvió algo que no es JSON (por ejemplo la página de
      // error 500 de Django). Ese contenido no se muestra al usuario: se
      // reemplaza por un mensaje entendible.
      data = { detail: MENSAJE_SERVIDOR_NO_DISPONIBLE }
    }
    const error = new Error('API error') as ErrorApi
    error.status = res.status
    error.data = data
    error.requiereRecarga = res.status === 409

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

// Tipos administrativos. Los códigos de estado pertenecen al backend; las
// etiquetas legibles que devuelve la API se conservan como texto.
export type CodigoEstadoServicio =
  | 'SOLICITADO'
  | 'EN_CURSO'
  | 'FINALIZADO'
  | 'CANCELADO'

export type CodigoEstadoComponente =
  | 'PENDIENTE'
  | 'EN_REVISION'
  | 'COTIZANDO'
  | 'ESPERANDO_APROBACION'
  | 'OPERARIO_TRABAJANDO'
  | 'EN_PRUEBAS'
  | 'LISTO_PARA_ENTREGA'
  | 'RECHAZADO'

export type TipoServicio = 'DIAGNOSTICO' | 'REPARACION' | 'MANTENIMIENTO' | 'PRUEBA' | 'OTRO'
export type TipoCotizacion = 'INICIAL' | 'ADICIONAL'
export type EstadoCotizacion = 'PENDIENTE' | 'APROBADA' | 'RECHAZADA'
export type ResultadoAprobacion = 'APROBADA' | 'RECHAZADA'
export type MedioAprobacion = 'WEB' | 'WHATSAPP' | 'LLAMADA' | 'PRESENCIAL' | 'OTRO'
export type CanalCotizacion = 'WEB' | 'WHATSAPP' | ''

export interface ClienteAdministrativo {
  id: number
  nombre: string
  empresa: string
  telefono: string
  whatsapp: string
  email: string
  direccion: string
  ciudad: string
  fecha_creacion: string
}

export interface ComponenteAdministrativo {
  id: number
  servicio: number
  tipo: string
  marca: string
  referencia: string
  descripcion: string
  cantidad: number
  estado: string
  fase: string
  trabajo_iniciado: boolean
  fecha_inicio_trabajo: string | null
  fecha_finalizacion: string | null
  motivo_finalizacion: string
  motivo_espera: string | null
  etiqueta_estado?: string
  etiqueta_fase?: string
  historial?: HistorialComponente[]
  acciones_disponibles?: string[]
  estados_seleccionables?: CodigoEstadoComponente[]
}

export interface HistorialComponente {
  id: number
  estado_anterior: string
  estado_nuevo: string
  fase_registrada: string
  comentario: string
  fecha: string
  usuario: string | null
}

export interface DetalleCotizacion {
  id?: number
  descripcion: string
  valor: string | number
  cantidad: number
}

export interface AprobacionServicio {
  id: number
  cotizacion: number
  resultado: ResultadoAprobacion
  medio: MedioAprobacion
  fecha: string
  usuario_registro: string | null
  observacion: string
  ip: string | null
  fecha_registro: string
}

export interface CotizacionAdministrativa {
  id: number
  servicio?: number
  numero: string
  tipo: TipoCotizacion
  descripcion: string
  total: string
  estado: EstadoCotizacion
  fecha_creacion: string
  observaciones: string
  creada_por: string | null
  componente: number | null
  etiqueta_componente: string
  es_bloqueante: boolean
  canal: CanalCotizacion
  detalles: DetalleCotizacion[]
  aprobaciones: AprobacionServicio[]
  reemplaza_a: number | null
  acciones_disponibles: string[]
  versiones: number[]
}

export interface HistorialServicio {
  id: number
  servicio: number
  estado: CodigoEstadoServicio | string
  comentario: string
  fecha: string
  usuario: string | null
  visible_cliente: boolean
}

export type TipoFotografia = 'RECEPCION' | 'DIAGNOSTICO' | 'REPARACION' | 'PRUEBA' | 'OTRO'

export interface Fotografia {
  id: number
  servicio: number
  url: string
  descripcion: string
  tipo: TipoFotografia | string
  visible_cliente: boolean
  fecha: string
  subida_por: string | null
}

export interface RegistroTecnico {
  id: number
  diagnostico: string
  trabajo_realizado: string
  resultado_pruebas: string
  recomendaciones: string
  observaciones: string
  creado_por: string | null
  actualizado_por: string | null
  fecha_creacion: string
  fecha_actualizacion: string
}

export interface ServicioResumenAdministrativo {
  id: number
  codigo: string
  cliente: { nombre: string; empresa: string }
  tipo_servicio: string
  estado: string
  entregar_en_banco: boolean
  avisar_para_coordinar: boolean
  recoger: boolean
  fecha_solicitud: string
}

export interface ResumenCierre {
  puede_finalizar: boolean
  motivo: string
  [clave: string]: unknown
}

export interface SeguimientoAdministrativo {
  disponible: boolean
  acciones: Array<'copiar' | 'abrir'>
  enlace: string | null
}

export interface ServicioAdministrativo extends ServicioResumenAdministrativo {
  cliente: ClienteAdministrativo
  descripcion_solicitud: string
  entregar_en_banco: boolean
  avisar_para_coordinar: boolean
  recoger: boolean
  fecha_recepcion: string | null
  fecha_finalizacion: string | null
  fecha_entrega: string | null
  observaciones_internas: string
  activo: boolean
  componentes: ComponenteAdministrativo[]
  cotizaciones: CotizacionAdministrativa[]
  historial: HistorialServicio[]
  fotografias: Fotografia[]
  registro_tecnico: RegistroTecnico | null
  resumen_cierre: ResumenCierre
  acciones_disponibles: string[]
  seguimiento: SeguimientoAdministrativo
}

export interface MensajeWhatsApp {
  clave: string
  ambito: 'SERVICIO' | 'COMPONENTE'
  etiqueta: string
  estado: string
  etiqueta_estado: string
  texto: string | null
  aviso: string | null
}

export interface RespuestaWhatsApp {
  codigo: string
  abierto: boolean
  numero_destino: string | null
  aviso: string | null
  mensajes: MensajeWhatsApp[]
}

export interface DashboardAdministrativo {
  total_activos: number
  contadores: Partial<Record<CodigoEstadoServicio, number>> & Record<string, number>
  recientes: ServicioResumenAdministrativo[]
  pendientes_atencion: ServicioResumenAdministrativo[]
  definicion: Record<string, string>
}

export interface ListadoServiciosAdministrativo {
  count: number
  next: string | null
  previous: string | null
  page: number
  page_size: 10
  results: ServicioResumenAdministrativo[]
}

export interface ParametrosListadoServicios {
  search?: string
  estado?: CodigoEstadoServicio
  page?: number
  ordering?: 'fecha_solicitud' | '-fecha_solicitud' | 'codigo' | '-codigo' | 'estado' | '-estado' | 'cliente' | '-cliente' | 'empresa' | '-empresa'
}

export interface DatosComponente {
  tipo: string
  marca?: string
  referencia?: string
  descripcion?: string
  cantidad?: number
}

export interface DatosCotizacion {
  servicio: number
  componente?: number | null
  tipo: TipoCotizacion
  descripcion?: string
  observaciones?: string
  es_bloqueante: boolean
  detalles: DetalleCotizacion[]
}

export interface DatosReenvioCotizacion {
  descripcion?: string
  observaciones?: string
  detalles?: DetalleCotizacion[]
}

export interface DatosAprobacionExterna {
  resultado: ResultadoAprobacion
  medio: Exclude<MedioAprobacion, 'WEB'>
  fecha?: string
  observacion?: string
}

export interface DatosRegistroTecnico {
  diagnostico?: string
  trabajo_realizado?: string
  resultado_pruebas?: string
  recomendaciones?: string
  observaciones?: string
}

export interface DatosFotografia {
  url: string
  descripcion?: string
  tipo: TipoFotografia
  visible_cliente?: boolean
}

export interface AccionCambiarEstadoComponente {
  estado: CodigoEstadoComponente
  comentario?: string
}

export interface RespuestaCotizacion {
  cotizacion_id: number
  resultado: ResultadoAprobacion
  canal: Exclude<CanalCotizacion, ''>
  observacion?: string
}

export type PasoPublico =
  | 'Recibido'
  | 'Revisión y cotización'
  | 'Pruebas'
  | 'Finalizado'

export interface HistorialComponenteSeguimiento {
  estado: string
  paso_publico: PasoPublico
  comentario: string
  fecha: string
}

export interface ComponenteSeguimiento {
  id: number
  servicio: number
  tipo: string
  marca: string
  referencia: string
  descripcion: string
  cantidad: number
  estado: string
  paso_publico: PasoPublico
  historial: HistorialComponenteSeguimiento[]
}

export interface CotizacionSeguimiento {
  id: number
  numero: string
  tipo: string
  descripcion: string
  estado: string
  total: string
  detalles: DetalleCotizacion[]
}

export interface HistorialSeguimiento {
  estado: string
  comentario: string
  fecha: string
}

export interface FotografiaSeguimiento {
  url: string
  descripcion: string
  tipo: string
  fecha: string
}

export interface ServicioSeguimiento {
  codigo: string
  tipo_servicio: string
  estado: string
  cancelado: boolean
  descripcion_solicitud: string
  fecha_solicitud: string
  fecha_recepcion: string | null
  fecha_finalizacion: string | null
  fecha_entrega: string | null
  componentes: ComponenteSeguimiento[]
  historial: HistorialSeguimiento[]
  fotografias: FotografiaSeguimiento[]
  cotizaciones_pendientes: CotizacionSeguimiento[]
}

function claveServicio(id: number) {
  return [...clavesAdministrativas.todas, 'servicio', id] as const
}

claveServicio.whatsapp = (id: number) => [...claveServicio(id), 'whatsapp'] as const

export const clavesAdministrativas = {
  todas: ['administrativo'] as const,
  dashboard: () => [...clavesAdministrativas.todas, 'dashboard'] as const,
  servicios: (parametros: ParametrosListadoServicios = {}) =>
    [...clavesAdministrativas.todas, 'servicios', {
      search: parametros.search ?? '',
      estado: parametros.estado ?? '',
      page: parametros.page ?? 1,
      ordering: parametros.ordering ?? '-fecha_solicitud',
    }] as const,
  servicio: claveServicio,
}

function construirQuery(parametros: ParametrosListadoServicios): string {
  const query = new URLSearchParams()
  if (parametros.search) query.set('search', parametros.search)
  if (parametros.estado) query.set('estado', parametros.estado)
  if (parametros.page && parametros.page > 1) query.set('page', String(parametros.page))
  if (parametros.ordering && parametros.ordering !== '-fecha_solicitud') query.set('ordering', parametros.ordering)
  const texto = query.toString()
  return texto ? `?${texto}` : ''
}

export const obtenerDashboardAdministrativo = () =>
  apiRequest<DashboardAdministrativo>('/api/admin/dashboard/')

export const listarServiciosAdministrativos = (parametros: ParametrosListadoServicios = {}) =>
  apiRequest<ListadoServiciosAdministrativo>(`/api/servicios/${construirQuery(parametros)}`)

export const obtenerServicioAdministrativo = (id: number) =>
  apiRequest<ServicioAdministrativo>(`/api/servicios/${id}/`)

export const obtenerMensajesWhatsapp = (servicioId: number) =>
  apiRequest<RespuestaWhatsApp>(`/api/servicios/${servicioId}/whatsapp/`)

async function enviar<T>(endpoint: string, method: string, body?: unknown): Promise<T> {
  return apiRequest<T>(endpoint, { method, body: body === undefined ? undefined : JSON.stringify(body) })
}

export const actualizarObservacionesServicio = (id: number, observaciones_internas: string) =>
  enviar<ServicioAdministrativo>(`/api/servicios/${id}/`, 'PATCH', { observaciones_internas })

export const crearComponente = (servicioId: number, datos: DatosComponente) =>
  enviar<ComponenteAdministrativo>(`/api/servicios/${servicioId}/componentes/`, 'POST', datos)

export const actualizarComponente = (servicioId: number, componenteId: number, datos: DatosComponente) =>
  enviar<ComponenteAdministrativo>(`/api/servicios/${servicioId}/componentes/${componenteId}/`, 'PATCH', datos)

export const eliminarComponente = (servicioId: number, componenteId: number) =>
  enviar<void>(`/api/servicios/${servicioId}/componentes/${componenteId}/`, 'DELETE')

export const responderCotizacion = (servicioId: number, componenteId: number, datos: RespuestaCotizacion) =>
  enviar<AprobacionServicio>(`/api/servicios/${servicioId}/componentes/${componenteId}/respuesta/`, 'POST', datos)

export const finalizarServicio = (servicioId: number, comentario?: string) =>
  enviar<ServicioAdministrativo>(`/api/servicios/${servicioId}/finalizar/`, 'POST', comentario ? { comentario } : {})

export const cancelarServicio = (servicioId: number, comentario: string) =>
  enviar<ServicioAdministrativo>(`/api/servicios/${servicioId}/cancelar/`, 'POST', { comentario })

export const registrarRecepcion = (servicioId: number, comentario?: string) =>
  enviar<ServicioAdministrativo>(`/api/servicios/${servicioId}/recepcion/`, 'POST', comentario ? { comentario } : {})

export const cambiarEstadoComponente = (
  servicioId: number,
  componenteId: number,
  datos: AccionCambiarEstadoComponente,
) =>
  enviar<ComponenteAdministrativo>(
    `/api/servicios/${servicioId}/componentes/${componenteId}/estado/`,
    'POST',
    datos,
  )

export const crearCotizacion = (datos: DatosCotizacion) =>
  enviar<CotizacionAdministrativa>('/api/cotizaciones/', 'POST', datos)

export const actualizarCotizacion = (id: number, datos: Partial<DatosCotizacion>) =>
  enviar<CotizacionAdministrativa>(`/api/cotizaciones/${id}/`, 'PATCH', datos)

export const reenviarCotizacion = (id: number, datos: DatosReenvioCotizacion) =>
  enviar<CotizacionAdministrativa>(`/api/cotizaciones/${id}/reenviar/`, 'POST', datos)

export const registrarAprobacionExterna = (cotizacionId: number, datos: DatosAprobacionExterna) =>
  enviar<AprobacionServicio>(`/api/cotizaciones/${cotizacionId}/aprobaciones/`, 'POST', datos)

export const obtenerSeguimiento = (token: string) =>
  apiRequest<ServicioSeguimiento>(`/api/seguimiento/${encodeURIComponent(token)}/`)

export const responderSeguimiento = (
  token: string,
  cotizacionId: number,
  resultado: ResultadoAprobacion,
  observacion = '',
) =>
  enviar<AprobacionServicio>(`/api/seguimiento/${encodeURIComponent(token)}/aprobar/`, 'POST', {
    cotizacion_id: cotizacionId,
    resultado,
    observacion,
  })

// Estos contratos quedan listos para los endpoints de T8; no alteran la sesión
// y mantienen el mismo adaptador HTTP cuando esas rutas estén disponibles.
export const crearRegistroTecnico = (servicioId: number, datos: DatosRegistroTecnico) =>
  enviar<RegistroTecnico>(`/api/servicios/${servicioId}/registro-tecnico/`, 'POST', datos)

export const actualizarRegistroTecnico = (servicioId: number, datos: DatosRegistroTecnico) =>
  enviar<RegistroTecnico>(`/api/servicios/${servicioId}/registro-tecnico/`, 'PATCH', datos)

export const crearFotografia = (servicioId: number, datos: DatosFotografia | FormData) =>
  apiRequest<Fotografia>(`/api/servicios/${servicioId}/fotografias/`, {
    method: 'POST',
    body: datos instanceof FormData ? datos : JSON.stringify(datos),
  })

export const actualizarFotografia = (servicioId: number, fotografiaId: number, datos: Partial<DatosFotografia>) =>
  enviar<Fotografia>(`/api/servicios/${servicioId}/fotografias/${fotografiaId}/`, 'PATCH', datos)

export const eliminarFotografia = (servicioId: number, fotografiaId: number) =>
  enviar<void>(`/api/servicios/${servicioId}/fotografias/${fotografiaId}/`, 'DELETE')
