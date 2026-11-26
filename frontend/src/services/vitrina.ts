import { apiRequest } from './api'

// Contratos de la vitrina pública (specs/013-vitrina-productos, §4.1).
// El backend es la autoridad de visibilidad, orden y filtros: el frontend solo
// consume `resultados` en el orden recibido y pinta las categorías del catálogo.

export interface CategoriaVitrina {
  slug: string
  nombre: string
}

export interface ImagenVitrina {
  url: string
  alt: string
}

export interface ProductoVitrina {
  clave: string
  nombre: string
  categoria: CategoriaVitrina
  descripcion: string
  imagen: ImagenVitrina
}

export interface RespuestaVitrina {
  categorias: CategoriaVitrina[]
  categoria: string | null
  carrusel: ImagenVitrina[]
  resultados: ProductoVitrina[]
}

export function obtenerVitrina(categoria: string | null = null): Promise<RespuestaVitrina> {
  // Sin parámetro se pide el catálogo completo. Un valor vacío
  // (`?categoria=`) se envía tal cual: el backend lo considera inválido.
  const buscar = categoria === null ? '' : `?categoria=${encodeURIComponent(categoria)}`
  return apiRequest<RespuestaVitrina>(`/api/productos/${buscar}`)
}

// Contratos del panel administrativo (specs/013-vitrina-productos, §4.2–4.4).
// El backend es la autoridad de validación, visibilidad, orden y archivos: el
// frontend solo envía los campos permitidos y muestra sus respuestas.

export interface ProductoAdministrativo {
  id: number
  nombre: string
  categoria: CategoriaVitrina
  descripcion: string
  imagen: ImagenVitrina
  visible: boolean
  fecha_creacion: string
  fecha_actualizacion: string
}

export interface RespuestaProductosAdministrativos {
  resultados: ProductoAdministrativo[]
}

export interface DatosProducto {
  nombre: string
  categoria: string
  descripcion: string
  imagen_alt: string
  visible: boolean
  imagen?: File
}

export type DatosNuevoProducto = Omit<DatosProducto, 'imagen'> & { imagen: File }
export type DatosActualizacionProducto = Partial<DatosProducto>

function construirFormData(
  datos: DatosProducto | DatosActualizacionProducto,
  archivo?: File,
): FormData {
  const formulario = new FormData()
  const campos = datos as Record<string, unknown>

  for (const campo of ['nombre', 'categoria', 'descripcion', 'imagen_alt'] as const) {
    const valor = campos[campo]
    if (typeof valor === 'string') formulario.set(campo, valor)
  }
  if (typeof campos.visible === 'boolean') formulario.set('visible', String(campos.visible))
  if (archivo) formulario.set('imagen', archivo)

  return formulario
}

function cuerpoJson(datos: DatosActualizacionProducto): string {
  const campos: Record<string, unknown> = {}
  const origen = datos as Record<string, unknown>

  for (const campo of ['nombre', 'categoria', 'descripcion', 'imagen_alt', 'visible'] as const) {
    if (origen[campo] !== undefined) campos[campo] = origen[campo]
  }
  return JSON.stringify(campos)
}

export const listarProductosAdministrativos = () =>
  apiRequest<RespuestaProductosAdministrativos>('/api/admin/productos/')

export const crearProductoAdministrativo = (datos: DatosNuevoProducto) =>
  apiRequest<ProductoAdministrativo>('/api/admin/productos/', {
    method: 'POST',
    body: construirFormData(datos, datos.imagen),
    csrf: true,
  })

export const actualizarProductoAdministrativo = (
  id: number,
  datos: DatosActualizacionProducto,
) =>
  apiRequest<ProductoAdministrativo>(`/api/admin/productos/${id}/`, {
    method: 'PATCH',
    body: datos.imagen
      ? construirFormData(datos, datos.imagen)
      : cuerpoJson(datos),
    csrf: true,
  })

export const eliminarProductoAdministrativo = (id: number) =>
  apiRequest<void>(`/api/admin/productos/${id}/`, {
    method: 'DELETE',
    csrf: true,
  })
