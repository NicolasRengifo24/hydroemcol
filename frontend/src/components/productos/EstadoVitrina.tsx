import { Link } from 'react-router-dom'
import { PackageOpen, SearchX, TriangleAlert } from 'lucide-react'

// Estados reutilizables de la vitrina (RF-VIT-06). Ninguno presenta datos
// parciales como si la consulta hubiera terminado correctamente.

export function CargaVitrina() {
  return (
    <div className="productos-estado" role="status">
      <p className="productos-estado__texto">Cargando productos…</p>
      <div className="productos-esqueletos" aria-hidden="true">
        {[0, 1, 2].map((posicion) => (
          <div className="productos-esqueleto" key={posicion}>
            <span className="productos-esqueleto__imagen" />
            <span className="productos-esqueleto__linea productos-esqueleto__linea--corta" />
            <span className="productos-esqueleto__linea" />
            <span className="productos-esqueleto__linea" />
          </div>
        ))}
      </div>
    </div>
  )
}

interface ErrorVitrinaProps {
  mensaje: string
  onReintentar: () => void
  reintentando?: boolean
}

export function ErrorVitrina({ mensaje, onReintentar, reintentando = false }: ErrorVitrinaProps) {
  return (
    <div className="productos-estado productos-estado--error" role="alert">
      <TriangleAlert size={26} aria-hidden="true" />
      <div>
        <h2>No pudimos cargar los productos</h2>
        <p>{mensaje}</p>
        <button
          type="button"
          className="productos-estado__accion"
          onClick={onReintentar}
          disabled={reintentando}
        >
          {reintentando ? 'Reintentando…' : 'Reintentar'}
        </button>
      </div>
    </div>
  )
}

interface VacioVitrinaProps {
  mensaje: string
  verTodos?: boolean
}

export function VacioVitrina({ mensaje, verTodos = false }: VacioVitrinaProps) {
  return (
    <div className="productos-estado productos-estado--vacio" role="status">
      <PackageOpen size={30} aria-hidden="true" />
      <h2>Sin productos para mostrar</h2>
      <p>{mensaje}</p>
      {verTodos ? (
        <Link className="productos-estado__accion" to="/productos">
          Ver todos los productos
        </Link>
      ) : null}
    </div>
  )
}

export function FiltroInvalidoVitrina({ mensaje }: { mensaje: string }) {
  return (
    <div className="productos-estado productos-estado--filtro" role="status">
      <SearchX size={30} aria-hidden="true" />
      <h2>Filtro no válido</h2>
      <p>{mensaje}</p>
      <Link className="productos-estado__accion" to="/productos">
        Ver todos los productos
      </Link>
    </div>
  )
}
