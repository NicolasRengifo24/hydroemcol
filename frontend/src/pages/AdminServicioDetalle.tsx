import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutacionesAdministrativas, useServicioAdministrativo } from '../hooks/useAdministrativo'
import type { CodigoEstadoComponente, CodigoEstadoServicio, ComponenteAdministrativo, ServicioAdministrativo } from '../services/api'
import { FotografiasPanel, RegistroTecnicoPanel } from '../components/AdminEvidencia'

const estadosServicio: Record<CodigoEstadoServicio, string> = { SOLICITADO: 'Solicitado', EN_CURSO: 'En curso', FINALIZADO: 'Finalizado', CANCELADO: 'Cancelado' }
const estadosComponente: Record<CodigoEstadoComponente, string> = { PENDIENTE: 'Pendiente', EN_REVISION: 'En revisión', COTIZANDO: 'Cotizando', ESPERANDO_APROBACION: 'Esperando aprobación', OPERARIO_TRABAJANDO: 'Operario trabajando', EN_PRUEBAS: 'En pruebas', LISTO_PARA_ENTREGA: 'Listo para entregar', RECHAZADO: 'Rechazado' }

function etiquetaServicio(estado: string) { return estadosServicio[estado as CodigoEstadoServicio] ?? estado }
function etiquetaComponente(estado: string) { return estadosComponente[estado as CodigoEstadoComponente] ?? estado }
function fecha(valor: string | null) { return valor ? new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(valor)) : '—' }
function errorLegible(error: unknown) {
  if (typeof error === 'object' && error !== null && 'data' in error) {
    const detalle = (error as { data?: { detail?: string } }).data?.detail
    if (detalle) return detalle
  }
  return 'La operación no pudo completarse. Verifica los datos e inténtalo de nuevo.'
}

function SelectorEstadoComponente({ componente, enviando, onAplicar }: { componente: ComponenteAdministrativo; enviando: boolean; onAplicar: (estado: CodigoEstadoComponente, comentario: string) => Promise<boolean> }) {
  const [estado, setEstado] = useState<CodigoEstadoComponente | ''>('')
  const [comentario, setComentario] = useState('')
  const opciones = componente.estados_seleccionables ?? []
  const requiereMotivo = estado === 'LISTO_PARA_ENTREGA' || estado === 'RECHAZADO' || componente.estado === 'LISTO_PARA_ENTREGA' || componente.estado === 'RECHAZADO'
  if (!opciones.length) return null
  const aplicar = async () => {
    if (!estado || (requiereMotivo && !comentario.trim())) return
    if (await onAplicar(estado, comentario.trim())) { setEstado(''); setComentario('') }
  }
  return <div className="admin-estado-selector">
    <div className="admin-estado-campo"><label htmlFor={`estado-componente-${componente.id}`}>Cambiar estado del componente</label><select id={`estado-componente-${componente.id}`} value={estado} onChange={(evento) => setEstado(evento.target.value as CodigoEstadoComponente)}><option value="">Elegir estado…</option>{opciones.map((codigo) => <option key={codigo} value={codigo}>{etiquetaComponente(codigo)}</option>)}</select></div>
    <div className="admin-estado-campo"><label htmlFor={`motivo-componente-${componente.id}`}>Motivo o comentario {requiereMotivo ? '(obligatorio)' : '(opcional)'}</label><textarea id={`motivo-componente-${componente.id}`} rows={2} value={comentario} onChange={(evento) => setComentario(evento.target.value)} /></div>
    <button className="admin-button admin-button--secondary" type="button" disabled={!estado || enviando || (requiereMotivo && !comentario.trim())} onClick={() => void aplicar()}>Cambiar estado</button>
  </div>
}

function AccionesServicio({ servicio, enviando, ejecutar }: { servicio: ServicioAdministrativo; enviando: boolean; ejecutar: (accion: 'finalizar' | 'cancelar', comentario: string) => Promise<boolean> }) {
  const [accion, setAccion] = useState<'finalizar' | 'cancelar' | ''>('')
  const [comentario, setComentario] = useState('')
  const confirmar = async () => { if (accion && (accion === 'finalizar' || comentario.trim()) && await ejecutar(accion, comentario.trim())) { setAccion(''); setComentario('') } }
  return <div className="admin-service-actions"><p>{servicio.resumen_cierre.motivo}</p><div className="admin-action-row"><button className="admin-button" disabled={enviando || !servicio.acciones_disponibles.includes('finalizar_servicio')} type="button" onClick={() => setAccion('finalizar')}>Finalizar servicio</button><button className="admin-button admin-button--secondary" disabled={enviando || !servicio.acciones_disponibles.includes('cancelar_servicio')} type="button" onClick={() => setAccion('cancelar')}>Cancelar servicio</button></div>{accion && <div className="admin-estado-campo"><label htmlFor="comentario-accion-servicio">Comentario {accion === 'cancelar' ? 'de cancelación (obligatorio)' : 'de finalización (opcional)'}</label><textarea id="comentario-accion-servicio" rows={3} required={accion === 'cancelar'} value={comentario} onChange={(evento) => setComentario(evento.target.value)} /><button className="admin-button" type="button" disabled={enviando || (accion === 'cancelar' && !comentario.trim())} onClick={() => void confirmar()}>Confirmar {accion === 'cancelar' ? 'cancelación' : 'finalización'}</button></div>}</div>
}

function AdminServicioDetalle() {
  const { id: idTexto } = useParams(); const id = Number(idTexto); const consulta = useServicioAdministrativo(id); const servicio = consulta.data; const mutaciones = useMutacionesAdministrativas(id)
  const [mensaje, setMensaje] = useState(''); const [error, setError] = useState('')
  const recargar = () => { void consulta.refetch() }
  const ejecutar = async (trabajo: () => Promise<unknown>, confirmacion?: string): Promise<boolean> => { if (confirmacion && !window.confirm(confirmacion)) return false; setError(''); setMensaje(''); try { await trabajo(); setMensaje('Operación completada.'); recargar(); return true } catch (razon) { const conflicto = (razon as { status?: number })?.status === 409; setError(`${errorLegible(razon)}${conflicto ? ' El detalle puede haber cambiado; recárgalo antes de reintentar.' : ''}`); return false } }
  if (!Number.isInteger(id) || id <= 0) return <section className="admin-page"><p className="admin-feedback admin-feedback--error" role="alert">El identificador del servicio no es válido.</p></section>
  if (consulta.isLoading) return <section className="admin-page"><p className="admin-feedback" role="status">Cargando detalle del servicio…</p></section>
  if (consulta.isError || !servicio) return <section className="admin-page"><div className="admin-feedback admin-feedback--error" role="alert"><p>{errorLegible(consulta.error)}</p><button className="admin-button" type="button" onClick={recargar}>Reintentar</button></div></section>
  const servicioActual = servicio
  return <section className="admin-page admin-detail" aria-labelledby="detalle-titulo"><div className="admin-page__intro"><div><Link className="admin-back-link" to="/admin/servicios">← Volver a servicios</Link><p className="admin-kicker">Detalle operativo</p><h1 id="detalle-titulo">{servicioActual.codigo}</h1><p className="admin-lead">{servicioActual.tipo_servicio} · {etiquetaServicio(servicioActual.estado)}</p></div><span className="admin-status admin-status--large">{etiquetaServicio(servicioActual.estado)}</span></div>{mensaje && <p className="admin-feedback admin-feedback--success" role="status">{mensaje}</p>}{error && <div className="admin-feedback admin-feedback--error" role="alert"><p>{error}</p><button className="admin-button admin-button--secondary" type="button" onClick={recargar}>Recargar detalle</button></div>}
    <div className="admin-detail-grid"><section className="admin-panel"><h2>Cliente</h2><dl className="admin-data-grid"><div><dt>Nombre</dt><dd>{servicioActual.cliente.nombre}</dd></div><div><dt>Empresa</dt><dd>{servicioActual.cliente.empresa || 'Particular'}</dd></div><div><dt>Teléfono</dt><dd>{servicioActual.cliente.telefono || '—'}</dd></div><div><dt>Correo</dt><dd>{servicioActual.cliente.email}</dd></div></dl></section><section className="admin-panel"><h2>Resumen y seguimiento</h2><dl className="admin-data-grid"><div><dt>Solicitud</dt><dd>{fecha(servicioActual.fecha_solicitud)}</dd></div><div><dt>Finalización</dt><dd>{fecha(servicioActual.fecha_finalizacion)}</dd></div><div><dt>Motivo de cierre</dt><dd>{servicioActual.resumen_cierre.motivo || '—'}</dd></div></dl></section></div>
    <section className="admin-panel" aria-labelledby="componentes-titulo"><h2 id="componentes-titulo">Componentes</h2>{servicioActual.componentes.length === 0 && <p className="admin-muted">No hay componentes registrados.</p>}<div className="admin-component-list">{servicioActual.componentes.map((componente) => <article className="admin-component-card" key={componente.id}><div className="admin-quote-heading"><div><h3>{componente.tipo}</h3><p>{[componente.marca, componente.referencia].filter(Boolean).join(' · ') || 'Sin marca o referencia'}</p></div><span className="admin-status">{componente.etiqueta_estado || etiquetaComponente(componente.estado)}</span></div><p>{componente.descripcion || 'Sin descripción.'} · Cantidad: {componente.cantidad}</p><p className="admin-muted">Fase: {componente.etiqueta_fase || componente.fase}{componente.motivo_espera ? ` · ${componente.motivo_espera}` : ''}</p><SelectorEstadoComponente componente={componente} enviando={mutaciones.cambiarEstadoComponente.isPending} onAplicar={(estado, comentario) => ejecutar(() => mutaciones.cambiarEstadoComponente.mutateAsync({ componenteId: componente.id, datos: { estado, comentario: comentario || undefined } }), `¿Cambiar el estado a ${etiquetaComponente(estado)}?`)} /></article>)}</div></section>
    <section className="admin-panel admin-panel--action"><h2>Acciones del servicio</h2><AccionesServicio servicio={servicioActual} enviando={mutaciones.finalizarServicio.isPending || mutaciones.cancelarServicio.isPending} ejecutar={(accion, comentario) => ejecutar(() => accion === 'finalizar' ? mutaciones.finalizarServicio.mutateAsync(comentario) : mutaciones.cancelarServicio.mutateAsync(comentario), accion === 'finalizar' ? '¿Finalizar el servicio? Esta acción es irreversible.' : '¿Cancelar el servicio?')} /></section>
    <section className="admin-panel"><h2>Cotizaciones y versiones</h2>{servicioActual.cotizaciones.length ? <div className="admin-quote-list">{servicioActual.cotizaciones.map((cotizacion) => <article className="admin-quote-card" key={cotizacion.id}><div className="admin-quote-heading"><div><h3>{cotizacion.numero}</h3><p>{cotizacion.etiqueta_componente} · {cotizacion.tipo}</p></div><span className="admin-status">{cotizacion.estado}</span></div><p>{cotizacion.descripcion || 'Sin descripción.'}</p><strong>Total neto: ${Number(cotizacion.total).toLocaleString('es-CO')}</strong></article>)}</div> : <p className="admin-muted">No hay cotizaciones registradas.</p>}</section>
    <section className="admin-panel"><h2>Historial del servicio</h2>{servicioActual.historial.length ? <ol className="admin-timeline">{servicioActual.historial.map((evento) => <li key={evento.id}><strong>{evento.estado}</strong><span>{evento.comentario}</span><small>{fecha(evento.fecha)} · {evento.usuario || 'Sistema'}</small></li>)}</ol> : <p className="admin-muted">No hay eventos en el historial.</p>}</section>
    <RegistroTecnicoPanel registro={servicioActual.registro_tecnico} servicioId={id} />
    <FotografiasPanel fotografias={servicioActual.fotografias} servicioId={id} />
  </section>
}
export default AdminServicioDetalle
