import { useMutation, useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import {
  obtenerSeguimiento,
  responderSeguimiento,
  type ErrorApi,
  type ResultadoAprobacion,
} from '../services/api'

function mensajeDeError(error: unknown): string {
  if (error && typeof error === 'object' && 'data' in error) {
    const data = (error as ErrorApi).data
    if (data && typeof data === 'object' && 'detail' in data && typeof data.detail === 'string') {
      return data.detail
    }
  }
  return 'No fue posible cargar el seguimiento. Intenta nuevamente.'
}

function fechaVisible(fecha: string | null): string {
  if (!fecha) return 'No registrada'
  return new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium' }).format(new Date(fecha))
}

function Seguimiento() {
  const { token } = useParams<{ token: string }>()
  const consulta = useQuery({
    queryKey: ['seguimiento', token],
    queryFn: () => obtenerSeguimiento(token!),
    enabled: Boolean(token),
  })
  const respuesta = useMutation({
    mutationFn: (resultado: ResultadoAprobacion) => responderSeguimiento(token!, resultado),
    onSuccess: () => consulta.refetch(),
  })

  if (!token) {
    return <section className="page seguimiento"><h1>Seguimiento de servicio</h1><p className="seguimiento__mensaje seguimiento__mensaje--error" role="alert">El enlace de seguimiento no es válido.</p></section>
  }

  if (consulta.isPending) {
    return <section className="page seguimiento"><h1>Seguimiento de servicio</h1><p className="seguimiento__mensaje" role="status">Cargando la información del servicio…</p></section>
  }

  if (consulta.isError) {
    return <section className="page seguimiento"><h1>Seguimiento de servicio</h1><div className="seguimiento__mensaje seguimiento__mensaje--error" role="alert"><p>{consulta.error instanceof Error && (consulta.error as ErrorApi).status === 404 ? 'No encontramos un servicio disponible para este enlace.' : mensajeDeError(consulta.error)}</p><button className="seguimiento__boton" type="button" onClick={() => consulta.refetch()}>Intentar de nuevo</button></div></section>
  }

  const servicio = consulta.data
  if (!servicio) return null

  return (
    <section className="page seguimiento">
      <h1>Seguimiento de servicio</h1>
      <div className="seguimiento__encabezado">
        <div>
          <p className="seguimiento__codigo">Servicio {servicio.codigo}</p>
          <p>{servicio.tipo_servicio}</p>
        </div>
        <p className="seguimiento__estado" aria-label={`Estado del servicio: ${servicio.estado}`}>{servicio.estado}</p>
      </div>

      <div className="seguimiento__grid">
        <section className="seguimiento__panel" aria-labelledby="componentes-titulo">
          <h2 id="componentes-titulo">Componentes registrados</h2>
          {servicio.componentes.length === 0 ? <p className="seguimiento__vacio">Aún no hay componentes registrados.</p> : <div className="seguimiento__componentes">{servicio.componentes.map((componente) => <article className="seguimiento__componente" key={componente.id}><h3>{componente.tipo}</h3><p>{componente.descripcion || 'Sin descripción adicional.'}</p><dl><div><dt>Estado</dt><dd>{componente.estado}</dd></div><div><dt>Fase</dt><dd>{componente.fase}</dd></div></dl></article>)}</div>}
        </section>

        <section className="seguimiento__panel" aria-labelledby="datos-titulo">
          <h2 id="datos-titulo">Datos del servicio</h2>
          <dl className="seguimiento__datos"><div><dt>Solicitud</dt><dd>{fechaVisible(servicio.fecha_solicitud)}</dd></div><div><dt>Recepción</dt><dd>{fechaVisible(servicio.fecha_recepcion)}</dd></div><div><dt>Finalización</dt><dd>{fechaVisible(servicio.fecha_finalizacion)}</dd></div></dl>
        </section>
      </div>

      {servicio.cotizaciones_pendientes.length > 0 && <section className="seguimiento__panel" aria-labelledby="cotizaciones-titulo"><h2 id="cotizaciones-titulo">Cotizaciones pendientes</h2><div className="seguimiento__cotizaciones">{servicio.cotizaciones_pendientes.map((cotizacion) => <article className="seguimiento__cotizacion" key={cotizacion.numero}><h3>{cotizacion.numero}</h3><p>{cotizacion.descripcion}</p><strong>Total: {cotizacion.total}</strong></article>)}</div><p>Selecciona una respuesta para registrar tu decisión.</p><div className="seguimiento__acciones"><button className="seguimiento__boton" type="button" disabled={respuesta.isPending} onClick={() => respuesta.mutate('APROBADA')}>Aprobar cotización</button><button className="seguimiento__boton seguimiento__boton--secundario" type="button" disabled={respuesta.isPending} onClick={() => respuesta.mutate('RECHAZADA')}>Rechazar cotización</button></div>{respuesta.isPending && <p role="status">Registrando tu respuesta…</p>}{respuesta.isError && <p className="seguimiento__mensaje--error" role="alert">{mensajeDeError(respuesta.error)}</p>}</section>}
      {respuesta.isSuccess && <p className="seguimiento__resultado" role="status">Tu respuesta fue registrada correctamente.</p>}

      {servicio.historial.length > 0 && <section className="seguimiento__panel" aria-labelledby="historial-titulo"><h2 id="historial-titulo">Actualizaciones visibles</h2><ul className="seguimiento__historial">{servicio.historial.map((registro, indice) => <li key={`${registro.fecha}-${indice}`}><strong>{registro.estado}</strong><span>{registro.comentario || 'Sin comentario.'}</span><time dateTime={registro.fecha}>{fechaVisible(registro.fecha)}</time></li>)}</ul></section>}
    </section>
  )
}

export default Seguimiento
