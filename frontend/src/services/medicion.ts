import { URL_SITIO } from '../config/sitio'

const CLAVES_UTM = [
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_term',
  'utm_content',
] as const

const CLAVE_SESION = 'hydroemcol:utm'
const ID_SCRIPT_PIXEL = 'meta-pixel-hydroemcol'
const URL_SCRIPT_PIXEL = 'https://connect.facebook.net/en_US/fbevents.js'
const URL_VITRINA = `${URL_SITIO}/productos`

export type Utm = Partial<Record<(typeof CLAVES_UTM)[number], string>>

export interface ProductoParaContacto {
  clave: string
  categoria: string
}

let utmMemoria: Utm = {}
let medicionInicializada = false

function esUtm(valor: unknown): valor is Utm {
  if (typeof valor !== 'object' || valor === null) return false

  const registro = valor as Record<string, unknown>
  return CLAVES_UTM.every((clave) => {
    const contenido = registro[clave]
    return contenido === undefined || typeof contenido === 'string'
  })
}

function almacenamientoDeSesion(): Storage | null {
  try {
    return typeof window === 'undefined' ? null : window.sessionStorage
  } catch {
    return null
  }
}

export function leerUtmDeUrl(search: string): Utm {
  const parametros = new URLSearchParams(search)
  const utm: Utm = {}

  for (const clave of CLAVES_UTM) {
    const valor = parametros.get(clave)?.trim()
    if (valor) utm[clave] = valor
  }

  return utm
}

export function fusionarUtm(previas: Utm, nuevas: Utm): Utm {
  const fusionadas: Utm = { ...previas }

  // La primera atribución gana; solo se completan las claves ausentes.
  for (const clave of CLAVES_UTM) {
    if (!fusionadas[clave] && nuevas[clave]) {
      fusionadas[clave] = nuevas[clave]
    }
  }

  return fusionadas
}

export function utmDeSesion(): Utm {
  const almacenamiento = almacenamientoDeSesion()

  try {
    const guardado = almacenamiento?.getItem(CLAVE_SESION)
    if (guardado) {
      const analizado: unknown = JSON.parse(guardado)
      if (esUtm(analizado)) {
        utmMemoria = fusionarUtm(utmMemoria, analizado)
      }
    }
  } catch {
    // sessionStorage puede fallar: se conserva solo la copia en memoria.
  }

  return { ...utmMemoria }
}

export function guardarUtmSesion(utm: Utm): Utm {
  utmMemoria = fusionarUtm(utmDeSesion(), utm)

  try {
    almacenamientoDeSesion()?.setItem(CLAVE_SESION, JSON.stringify(utmMemoria))
  } catch {
    // La medición no debe romper la vitrina si no hay almacenamiento.
  }

  return { ...utmMemoria }
}

function asegurarFbq(): void {
  if (typeof window === 'undefined' || typeof window.fbq === 'function') return

  const cola: unknown[][] = []
  const fbq = ((...argumentos: unknown[]) => {
    cola.push(argumentos)
  }) as Fbq
  fbq.queue = cola
  window.fbq = fbq
}

function registrar(...argumentos: unknown[]): void {
  try {
    if (typeof window === 'undefined' || typeof window.fbq !== 'function') return
    window.fbq(...argumentos)
  } catch {
    // Un Pixel bloqueado o mal cargado nunca interrumpe la navegación.
  }
}

export function inicializarMedicion(): void {
  if (medicionInicializada || typeof window === 'undefined') return

  const idPixel = import.meta.env.VITE_META_PIXEL_ID?.trim()
  if (!idPixel) return

  medicionInicializada = true

  try {
    asegurarFbq()

    if (!document.getElementById(ID_SCRIPT_PIXEL)) {
      const script = document.createElement('script')
      script.id = ID_SCRIPT_PIXEL
      script.async = true
      script.src = URL_SCRIPT_PIXEL
      document.head.appendChild(script)
    }

    // Solo init: la spec no autoriza PageView.
    registrar('init', idPixel)
  } catch {
    // La medición es opcional y no bloquea la aplicación.
  }
}

function parametrosUtm(utm: Utm): Record<string, unknown> {
  const parametros: Record<string, unknown> = {}

  for (const clave of CLAVES_UTM) {
    const valor = utm[clave]
    if (valor) parametros[clave] = valor
  }

  return parametros
}

export function parametrosViewContent(utm: Utm): Record<string, unknown> {
  return { content_url: URL_VITRINA, ...parametrosUtm(utm) }
}

export function parametrosContacto(
  producto: ProductoParaContacto,
  utm: Utm,
): Record<string, unknown> {
  return {
    origen: 'producto',
    content_category: producto.categoria,
    content_ids: [producto.clave],
    ...parametrosUtm(utm),
  }
}

export function enviarViewContent(utm: Utm = utmDeSesion()): void {
  registrar('track', 'ViewContent', parametrosViewContent(utm))
}

export function enviarContactoProducto(
  producto: ProductoParaContacto,
  utm: Utm = utmDeSesion(),
): void {
  registrar('track', 'Contact', parametrosContacto(producto, utm))
}
