import { Link } from 'react-router-dom'
import { useDashboardAdministrativo } from '../hooks/useAdministrativo'
import type { CodigoEstadoServicio, ServicioResumenAdministrativo } from '../services/api'

const estados: Array<{ codigo: CodigoEstadoServicio; etiqueta: string }> = [
  { codigo: 'SOLICITADO', etiqueta: 'Solicitados' }, { codigo: 'EN_REVISION', etiqueta: 'En revisión' },
  { codigo: 'COTIZANDO', etiqueta: 'Cotizando' }, { codigo: 'ESPERANDO_APROBACION', etiqueta: 'Esperando aprobación' },
  { codigo: 'EN_REPARACION', etiqueta: 'En reparación' }, { codigo: 'EN_PRUEBAS', etiqueta: 'En pruebas' },
  { codigo: 'FINALIZADO', etiqueta: 'Finalizados' }, { codigo: 'LISTO_PARA_ENTREGA', etiqueta: 'Listos para entrega' },
  { codigo: 'ENTREGADO', etiqueta: 'Entregados' }, { codigo: 'NO_APROBADO', etiqueta: 'No aprobados' }, { codigo: 'CANCELADO', etiqueta: 'Cancelados' },
]

function fechaLegible(fecha: string) {
  return new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium' }).format(new Date(fecha))
}

function errorLegible(error: unknown) {
  if (typeof error === 'object' && error !== null && 'data' in error) {
    const data = (error as { data?: { detail?: string } }).data
    if (data?.detail) return data.detail
  }
  return 'No se pudo cargar el resumen operativo.'
}

function ServicioResumen({ servicio }: { servicio: ServicioResumenAdministrativo }) {
  return <Link className="admin-list-item" to={`/admin/servicios/${servicio.id}`}><span><strong>{servicio.codigo}</strong><small>{servicio.cliente.nombre}{servicio.cliente.empresa ? ` · ${servicio.cliente.empresa}` : ''}</small></span><span className="admin-list-item__meta">{servicio.estado}<small>{fechaLegible(servicio.fecha_solicitud)}</small></span></Link>
}

function Admin() {
  const consulta = useDashboardAdministrativo()

  return (
    <section className="admin-page" aria-labelledby="dashboard-titulo">
      <div className="admin-page__intro">
        <div><p className="admin-kicker">Control de operación</p><h1 id="dashboard-titulo">Resumen operativo</h1><p className="admin-lead">Una lectura rápida de los servicios que requieren seguimiento técnico y administrativo.</p></div>
        <Link className="admin-button" to="/admin/servicios">Ver todos los servicios</Link>
      </div>
      {consulta.isLoading && <p className="admin-feedback" role="status">Cargando indicadores operativos…</p>}
      {consulta.isError && <div className="admin-feedback admin-feedback--error" role="alert"><p>{errorLegible(consulta.error)}</p><button className="admin-button" type="button" onClick={() => void consulta.refetch()}>Reintentar</button></div>}
      {consulta.isSuccess && (
        <>
          <section aria-labelledby="indicadores-titulo"><div className="admin-section-heading"><div><p className="admin-kicker">Datos del servidor</p><h2 id="indicadores-titulo">Indicadores activos</h2></div><span className="admin-section-note">Solo servicios activos</span></div><div className="admin-metrics"><Link className="admin-metric admin-metric--total" to="/admin/servicios"><span>Total activos</span><strong>{consulta.data.total_activos}</strong></Link>{estados.map((estado) => <Link className="admin-metric" key={estado.codigo} to={`/admin/servicios?estado=${estado.codigo}`}><span>{estado.etiqueta}</span><strong>{consulta.data.contadores[estado.codigo] ?? 0}</strong></Link>)}</div></section>
          <div className="admin-dashboard-grid"><section className="admin-panel" aria-labelledby="recientes-titulo"><div className="admin-section-heading"><h2 id="recientes-titulo">Servicios recientes</h2><span>Últimos 10</span></div>{consulta.data.recientes.length ? <div className="admin-list">{consulta.data.recientes.map((servicio) => <ServicioResumen key={servicio.id} servicio={servicio} />)}</div> : <p className="admin-muted">No hay servicios activos recientes.</p>}</section><section className="admin-panel" aria-labelledby="pendientes-titulo"><div className="admin-section-heading"><h2 id="pendientes-titulo">Pendientes de atención</h2><span>Prioridad operativa</span></div>{consulta.data.pendientes_atencion.length ? <div className="admin-list">{consulta.data.pendientes_atencion.map((servicio) => <ServicioResumen key={servicio.id} servicio={servicio} />)}</div> : <p className="admin-muted">No hay servicios pendientes de atención.</p>}</section></div>
        </>
      )}
    </section>
  )
}

export default Admin
