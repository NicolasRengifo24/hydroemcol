import { useEffect, useRef } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import Seo from '../seo/Seo'
import { useVitrina } from '../hooks/useVitrina'
import type { ErrorApi } from '../services/api'
import { mensajeDeError } from '../services/errores'
import type { CategoriaVitrina } from '../services/vitrina'
import {
  enviarViewContent,
  guardarUtmSesion,
  leerUtmDeUrl,
} from '../services/medicion'
import { HeroProductos } from '../components/productos/HeroProductos'
import { TarjetaProducto } from '../components/productos/TarjetaProducto'
import {
  CargaVitrina,
  ErrorVitrina,
  FiltroInvalidoVitrina,
  VacioVitrina,
} from '../components/productos/EstadoVitrina'
import '../components/productos/productos.css'

const MENSAJE_ERROR =
  'No pudimos cargar los productos. Revisa tu conexión e inténtalo de nuevo.'

// La categoría puede llegar en el error 400 del backend. Se usa solo para
// mantener visible el catálogo de filtros; los productos nunca se muestran.
function categoriasDelError(error: unknown): CategoriaVitrina[] {
  if (typeof error !== 'object' || error === null) return []

  const datos = (error as { data?: unknown }).data
  if (typeof datos !== 'object' || datos === null) return []

  const categorias = (datos as { categorias?: unknown }).categorias
  if (!Array.isArray(categorias)) return []

  return categorias.filter(
    (categoria): categoria is CategoriaVitrina =>
      typeof categoria === 'object' &&
      categoria !== null &&
      typeof (categoria as CategoriaVitrina).slug === 'string' &&
      typeof (categoria as CategoriaVitrina).nombre === 'string',
  )
}

function Productos() {
  const [parametros] = useSearchParams()
  const categoria = parametros.has('categoria') ? (parametros.get('categoria') ?? '') : null
  const { data, error, isPending, isPlaceholderData, isError, isFetching, refetch } =
    useVitrina(categoria)

  // La guardia evita duplicar ViewContent al cambiar de filtro o en StrictMode.
  const medicionEnviada = useRef(false)
  useEffect(() => {
    if (medicionEnviada.current) return
    medicionEnviada.current = true

    const utm = guardarUtmSesion(leerUtmDeUrl(parametros.toString()))
    enviarViewContent(utm)
  }, [parametros])

  // Los filtros se pintan desde el catálogo del backend. React Query conserva
  // la respuesta anterior mientras carga otro filtro, así que la navegación no
  // desaparece; sus resultados no se muestran hasta que la consulta termina.
  const categorias =
    data?.categorias.length ? data.categorias : categoriasDelError(error)

  const cargando = isPending || isPlaceholderData
  const errorApi = error as ErrorApi | null
  const filtroInvalido = isError && errorApi?.status === 400
  const mensaje = mensajeDeError(error, MENSAJE_ERROR)

  return (
    <div className="productos">
      <Seo ruta="/productos" />

      <HeroProductos />

      <div className="productos__contenido">
        <header className="productos__encabezado">
          <p className="productos__eyebrow">Catálogo técnico</p>
          <h1 className="productos__titulo">Componentes y repuestos hidráulicos</h1>
          <p className="productos__descripcion">
            Encuentra soluciones hidráulicas para mantenimiento, reparación y
            operación industrial. Consulta disponibilidad y especificaciones con
            nuestro equipo técnico.
          </p>
        </header>

        <nav className="productos__filtros" aria-label="Filtrar productos por categoría">
          <Link
            className="productos__filtro"
            to="/productos"
            aria-current={categoria === null ? 'page' : undefined}
          >
            Todos
          </Link>
          {categorias.map((item) => (
            <Link
              key={item.slug}
              className="productos__filtro"
              to={`/productos?categoria=${encodeURIComponent(item.slug)}`}
              aria-current={categoria === item.slug ? 'page' : undefined}
            >
              {item.nombre}
            </Link>
          ))}
        </nav>

        {cargando ? <CargaVitrina /> : null}

        {filtroInvalido ? <FiltroInvalidoVitrina mensaje={mensaje} /> : null}

        {isError && !filtroInvalido ? (
          <ErrorVitrina
            mensaje={mensaje}
            reintentando={isFetching}
            onReintentar={() => {
              void refetch()
            }}
          />
        ) : null}

        {data && !cargando ? (
          data.resultados.length === 0 ? (
              <VacioVitrina
                mensaje={
                  categoria === null
                    ? 'Todavía no hay productos publicados.'
                    : 'No hay productos en esta categoría.'
                }
                verTodos={categoria !== null}
              />
          ) : (
            <ul className="productos__cuadricula" aria-label="Productos disponibles">
              {data.resultados.map((producto) => (
                <li className="productos__item" key={producto.clave}>
                  <TarjetaProducto producto={producto} />
                </li>
              ))}
            </ul>
          )
        ) : null}
      </div>
    </div>
  )
}

export default Productos
