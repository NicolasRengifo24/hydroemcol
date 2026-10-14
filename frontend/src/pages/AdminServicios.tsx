import type { FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useServiciosAdministrativos } from '../hooks/useAdministrativo'
import type { CodigoEstadoServicio, ParametrosListadoServicios, ServicioResumenAdministrativo } from '../services/api'

const estados: Array<{ codigo: CodigoEstadoServicio; etiqueta: string }> = [
  { codigo: 'SOLICITADO', etiqueta: 'Solicitado' },
  { codigo: 'EN_REVISION', etiqueta: 'En revisión' },
  { codigo: 'COTIZANDO', etiqueta: 'Cotizando' },
  { codigo: 'ESPERANDO_APROBACION', etiqueta: 'Esperando aprobación' },
  { codigo: 'EN_REPARACION', etiqueta: 'En reparación' },
  { codigo: 'EN_PRUEBAS', etiqueta: 'En pruebas' },
  { codigo: 'FINALIZADO', etiqueta: 'Finalizado' },
  { codigo: 'LISTO_PARA_ENTREGA', etiqueta: 'Listo para entrega' },
  { codigo: 'ENTREGADO', etiqueta: 'Entregado' },
  { codigo: 'NO_APROBADO', etiqueta: 'No aprobado' },
  { codigo: 'CANCELADO', etiqueta: 'Cancelado' },
]

const ordenamientos: Array<{ valor: NonNullable<ParametrosListadoServicios['ordering']>; etiqueta: string }> = [
  { valor: '-fecha_solicitud', etiqueta: 'Más recientes' },
  { valor: 'fecha_solicitud', etiqueta: 'Más antiguos' },
  { valor: 'codigo', etiqueta: 'Código A-Z' },
  { valor: '-codigo', etiqueta: 'Código Z-A' },
  { valor: 'estado', etiqueta: 'Estado A-Z' },
  { valor: '-estado', etiqueta: 'Estado Z-A' },
  { valor: 'cliente', etiqueta: 'Cliente A-Z' },
  { valor: '-cliente', etiqueta: 'Cliente Z-A' },
  { valor: 'empresa', etiqueta: 'Empresa A-Z' },
  { valor: '-empresa', etiqueta: 'Empresa Z-A' },
]

function fechaLegible(fecha: string) {
  return new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium' }).format(new Date(fecha))
}

function errorLegible(error: unknown) {
  if (typeof error === 'object' && error !== null && 'data' in error) {
    const data = (error as { data?: { detail?: string } }).data
    if (data?.detail) return data.detail
  }
  return 'No se pudo cargar el listado de servicios.'
}

function ServicioCard({ servicio }: { servicio: ServicioResumenAdministrativo }) {
  return (
    <article className="admin-service-card">
      <div className="admin-service-card__topline">
        <Link to={`/admin/servicios/${servicio.id}`}><strong>{servicio.codigo}</strong></Link>
        <span className="admin-status">{servicio.estado}</span>
      </div>
      <dl className="admin-service-card__details">
        <div><dt>Cliente</dt><dd>{servicio.cliente.nombre}</dd></div>
        <div><dt>Empresa</dt><dd>{servicio.cliente.empresa || 'Particular'}</dd></div>
        <div><dt>Servicio</dt><dd>{servicio.tipo_servicio}</dd></div>
        <div><dt>Solicitud</dt><dd>{fechaLegible(servicio.fecha_solicitud)}</dd></div>
      </dl>
    </article>
  )
}

function AdminServicios() {
  const [searchParams, setSearchParams] = useSearchParams()
  const search = searchParams.get('search') ?? ''
  const estado = (searchParams.get('estado') ?? '') as CodigoEstadoServicio | ''
  const ordering = (searchParams.get('ordering') ?? '-fecha_solicitud') as NonNullable<ParametrosListadoServicios['ordering']>
  const page = Math.max(1, Number(searchParams.get('page') ?? '1') || 1)
  const parametros: ParametrosListadoServicios = { search, page, ordering }
  if (estado) parametros.estado = estado
  const consulta = useServiciosAdministrativos(parametros)
  const totalPaginas = consulta.data ? Math.max(1, Math.ceil(consulta.data.count / consulta.data.page_size)) : 1

  function actualizarParametros(cambios: Record<string, string>) {
    const nuevos = new URLSearchParams(searchParams)
    Object.entries(cambios).forEach(([clave, valor]) => {
      if (valor) nuevos.set(clave, valor)
      else nuevos.delete(clave)
    })
    setSearchParams(nuevos)
  }

  function buscar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const datos = new FormData(evento.currentTarget)
    actualizarParametros({ search: String(datos.get('search') ?? '').trim(), page: '1' })
  }

  function limpiarFiltros() {
    setSearchParams({})
  }

  return (
    <section className="admin-page" aria-labelledby="servicios-titulo">
      <div className="admin-page__intro">
        <div>
          <p className="admin-kicker">Operación</p>
          <h1 id="servicios-titulo">Servicios</h1>
          <p className="admin-lead">Busca y prioriza las solicitudes activas de Hidroemcol.</p>
        </div>
        <span className="admin-page__context">20 registros por página</span>
      </div>

      <form className="admin-filters" onSubmit={buscar}>
        <div className="admin-field admin-field--search">
          <label htmlFor="buscar-servicios">Buscar servicio</label>
          <input key={search} id="buscar-servicios" name="search" type="search" defaultValue={search} placeholder="Código, cliente o empresa" />
        </div>
        <div className="admin-field">
          <label htmlFor="filtro-estado">Estado</label>
          <select id="filtro-estado" value={estado} onChange={(evento) => actualizarParametros({ estado: evento.target.value, page: '1' })}>
            <option value="">Todos los estados</option>
            {estados.map((opcion) => <option key={opcion.codigo} value={opcion.codigo}>{opcion.etiqueta}</option>)}
          </select>
        </div>
        <div className="admin-field">
          <label htmlFor="orden-servicios">Ordenar por</label>
          <select id="orden-servicios" value={ordering} onChange={(evento) => actualizarParametros({ ordering: evento.target.value, page: '1' })}>
            {ordenamientos.map((opcion) => <option key={opcion.valor} value={opcion.valor}>{opcion.etiqueta}</option>)}
          </select>
        </div>
        <button className="admin-button" type="submit">Buscar</button>
        {(search || estado || page > 1 || ordering !== '-fecha_solicitud') && <button className="admin-button admin-button--secondary" type="button" onClick={limpiarFiltros}>Limpiar</button>}
      </form>

      {consulta.isLoading && <p className="admin-feedback" role="status">Cargando servicios…</p>}
      {consulta.isError && <div className="admin-feedback admin-feedback--error" role="alert"><p>{errorLegible(consulta.error)}</p><button className="admin-button" type="button" onClick={() => void consulta.refetch()}>Reintentar</button></div>}
      {consulta.isSuccess && consulta.data.results.length === 0 && <div className="admin-empty"><h2>No encontramos servicios</h2><p>Prueba con otra búsqueda o limpia los filtros aplicados.</p><button className="admin-button admin-button--secondary" type="button" onClick={limpiarFiltros}>Limpiar filtros</button></div>}
      {consulta.isSuccess && consulta.data.results.length > 0 && (
        <>
          <p className="admin-result-summary" role="status">{consulta.data.count} servicio{consulta.data.count === 1 ? '' : 's'} encontrado{consulta.data.count === 1 ? '' : 's'}. Página {consulta.data.page} de {totalPaginas}.</p>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <caption className="sr-only">Servicios activos</caption>
              <thead><tr><th scope="col">Código</th><th scope="col">Cliente / empresa</th><th scope="col">Servicio</th><th scope="col">Estado</th><th scope="col">Solicitud</th></tr></thead>
<tbody>{consulta.data.results.map((servicio) => <tr key={servicio.id}><th scope="row"><Link to={`/admin/servicios/${servicio.id}`}>{servicio.codigo}</Link></th><td>{servicio.cliente.nombre}<small>{servicio.cliente.empresa || 'Particular'}</small></td><td>{servicio.tipo_servicio}</td><td><span className="admin-status">{servicio.estado}</span></td><td>{fechaLegible(servicio.fecha_solicitud)}</td></tr>)}</tbody>
            </table>
          </div>
          <div className="admin-cards" aria-label="Servicios activos en tarjetas">{consulta.data.results.map((servicio) => <ServicioCard key={servicio.id} servicio={servicio} />)}</div>
          <nav className="admin-pagination" aria-label="Paginación de servicios">
            <button className="admin-button admin-button--secondary" type="button" disabled={page <= 1} onClick={() => actualizarParametros({ page: String(page - 1) })}>Anterior</button>
            <span>Página {page} de {totalPaginas}</span>
            <button className="admin-button admin-button--secondary" type="button" disabled={page >= totalPaginas} onClick={() => actualizarParametros({ page: String(page + 1) })}>Siguiente</button>
          </nav>
        </>
      )}
    </section>
  )
}

export default AdminServicios
