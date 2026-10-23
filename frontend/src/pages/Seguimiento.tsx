import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { CircuitoValvulas } from "../components/seguimiento/CircuitoValvulas";
import {
  obtenerSeguimiento,
  responderSeguimiento,
  type ErrorApi,
  type ResultadoAprobacion,
  type ServicioSeguimiento,
} from "../services/api";

function mensajeDeError(error: unknown): string {
  if (error && typeof error === "object" && "data" in error) {
    const data = (error as ErrorApi).data;
    if (
      data &&
      typeof data === "object" &&
      "detail" in data &&
      typeof data.detail === "string"
    ) {
      return data.detail;
    }
  }
  return "No fue posible cargar el seguimiento. Intenta nuevamente.";
}

function fechaVisible(fecha: string | null): string {
  if (!fecha) return "No registrada";
  return new Intl.DateTimeFormat("es-CO", { dateStyle: "medium" }).format(
    new Date(fecha),
  );
}

function comentarioDeRecepcion(
  fechaRecepcion: string | null,
  historial: ServicioSeguimiento["historial"],
): string {
  if (!fechaRecepcion) return "";
  const inicio = new Date(fechaRecepcion).getTime();
  return historial.find((registro) => new Date(registro.fecha).getTime() >= inicio)?.comentario || "";
}

function Seguimiento() {
  const { token } = useParams<{ token: string }>();
  const consulta = useQuery({
    queryKey: ["seguimiento", token],
    queryFn: () => obtenerSeguimiento(token!),
    enabled: Boolean(token),
  });
  const respuesta = useMutation({
    mutationFn: ({
      cotizacionId,
      resultado,
    }: {
      cotizacionId: number;
      resultado: ResultadoAprobacion;
    }) => responderSeguimiento(token!, cotizacionId, resultado),
    onSuccess: () => consulta.refetch(),
  });

  if (!token) {
    return (
      <section className="page seguimiento">
        <h1>Seguimiento de servicio</h1>
        <p
          className="seguimiento__mensaje seguimiento__mensaje--error"
          role="alert"
        >
          El enlace de seguimiento no es válido.
        </p>
      </section>
    );
  }

  if (consulta.isPending) {
    return (
      <section className="page seguimiento">
        <h1>Seguimiento de servicio</h1>
        <p className="seguimiento__mensaje" role="status">
          Cargando la información del servicio…
        </p>
      </section>
    );
  }

  if (consulta.isError) {
    return (
      <section className="page seguimiento">
        <h1>Seguimiento de servicio</h1>
        <div
          className="seguimiento__mensaje seguimiento__mensaje--error"
          role="alert"
        >
          <p>
            {consulta.error instanceof Error &&
            (consulta.error as ErrorApi).status === 404
              ? "No encontramos un servicio disponible para este enlace."
              : mensajeDeError(consulta.error)}
          </p>
          <button
            className="seguimiento__boton"
            type="button"
            onClick={() => consulta.refetch()}
          >
            Intentar de nuevo
          </button>
        </div>
      </section>
    );
  }

  const servicio = consulta.data;
  if (!servicio) return null;

  return (
    <section className="page seguimiento">
      <h1>Seguimiento de servicio</h1>
      <div className="seguimiento__encabezado">
        <div>
          <p className="seguimiento__codigo">Servicio {servicio.codigo}</p>
          <p>{servicio.tipo_servicio}</p>
        </div>
        <p
          className="seguimiento__estado"
          aria-label={`Estado del servicio: ${servicio.estado}`}
        >
          {servicio.estado}
        </p>
        {servicio.cancelado && (
          <p className="seguimiento__vacio" role="status">
            Este servicio fue cancelado. Si tienes dudas, escríbenos por
            WhatsApp.
          </p>
        )}
      </div>

      <div className="seguimiento__grid">
        <section
          className="seguimiento__panel"
          aria-labelledby="componentes-titulo"
        >
          <h2 id="componentes-titulo">Componentes registrados</h2>
          {servicio.componentes.length === 0 ? (
            <p className="seguimiento__vacio">
              Aún no hay componentes registrados.
            </p>
          ) : (
            <div className="seguimiento__componentes">
              {servicio.componentes.map((componente) => (
                <article
                  className="seguimiento__componente"
                  key={componente.id}
                >
                  <h3>{componente.tipo}</h3>
                  <p>
                    {componente.descripcion || "Sin descripción adicional."}
                  </p>
                  <CircuitoValvulas
                    paso={componente.paso_publico}
                    tipo={componente.tipo}
                    estado={componente.estado}
                    historial={componente.historial}
                  />
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="seguimiento__panel" aria-labelledby="datos-titulo">
          <h2 id="datos-titulo">Datos del servicio</h2>
          <dl className="seguimiento__datos">
            <div>
              <dt>Solicitud</dt>
              <dd>{fechaVisible(servicio.fecha_solicitud)}</dd>
            </div>
            <div>
              <dt>Recepción</dt>
              <dd>{fechaVisible(servicio.fecha_recepcion)}</dd>
            </div>
            <div>
              <dt>Finalización</dt>
              <dd>{fechaVisible(servicio.fecha_finalizacion)}</dd>
            </div>
          </dl>
          {servicio.fecha_recepcion && (
            <div className="seguimiento__recepcion" role="status">
              <strong>Recepción registrada</strong>
              <p>
                {comentarioDeRecepcion(servicio.fecha_recepcion, servicio.historial) ||
                  "El equipo confirmó la recepción de tu componente."}
              </p>
            </div>
          )}
        </section>
      </div>

      {servicio.cotizaciones_pendientes.length > 0 && (
        <section
          className="seguimiento__panel seguimiento__panel--cotizaciones"
          aria-labelledby="cotizaciones-titulo"
        >
          <h2 id="cotizaciones-titulo">Cotizaciones pendientes</h2>
          <div className="seguimiento__cotizaciones">
            {servicio.cotizaciones_pendientes.map((cotizacion) => (
              <article
                className={`seguimiento__cotizacion${cotizacion.es_bloqueante ? " seguimiento__cotizacion--bloqueante" : ""}`}
                key={cotizacion.id}
              >
                <div className="seguimiento__cotizacion-encabezado">
                  <div>
                    <h3>{cotizacion.numero}</h3>
                    <p>{cotizacion.tipo}</p>
                  </div>
                  {cotizacion.es_bloqueante && (
                    <span className="seguimiento__cotizacion-alerta">
                      Requerida para continuar
                    </span>
                  )}
                </div>
                <p>{cotizacion.descripcion}</p>
                <strong>
                  Total: ${Number(cotizacion.total).toLocaleString("es-CO")}
                </strong>
                {cotizacion.es_bloqueante && (
                  <p className="seguimiento__cotizacion-nota">
                    Esta cotización es necesaria para continuar el trabajo sobre tu componente.
                  </p>
                )}
                <details className="seguimiento__cotizacion-detalles">
                  <summary>Ver detalles de la cotización</summary>
                  {cotizacion.observaciones && (
                    <div className="seguimiento__cotizacion-observaciones">
                      <strong>Observaciones del asesor</strong>
                      <p>{cotizacion.observaciones}</p>
                    </div>
                  )}
                  {cotizacion.detalles.length > 0 && (
                    <ul>
                      {cotizacion.detalles.map((detalle) => (
                        <li key={detalle.id ?? `${detalle.descripcion}-${detalle.cantidad}`}>
                          <span>{detalle.descripcion}</span>
                          <span>
                            {detalle.cantidad} × ${Number(detalle.valor).toLocaleString("es-CO")}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </details>
                <div className="seguimiento__acciones">
                  <button
                    className="seguimiento__boton"
                    type="button"
                    disabled={respuesta.isPending}
                    onClick={() =>
                      respuesta.mutate({
                        cotizacionId: cotizacion.id,
                        resultado: "APROBADA",
                      })
                    }
                  >
                    Aprobar cotización
                  </button>
                  <button
                    className="seguimiento__boton seguimiento__boton--secundario"
                    type="button"
                    disabled={respuesta.isPending}
                    onClick={() =>
                      respuesta.mutate({
                        cotizacionId: cotizacion.id,
                        resultado: "RECHAZADA",
                      })
                    }
                  >
                    Rechazar cotización
                  </button>
                </div>
              </article>
            ))}
          </div>
          {respuesta.isPending && (
            <p role="status">Registrando tu respuesta…</p>
          )}
          {respuesta.isError && (
            <p className="seguimiento__mensaje--error" role="alert">
              {mensajeDeError(respuesta.error)}
            </p>
          )}
        </section>
      )}
      {servicio.fotografias.length > 0 && (
        <details className="seguimiento__panel seguimiento__panel--fotografias">
          <summary>Ver evidencias fotográficas ({servicio.fotografias.length})</summary>
          <p className="seguimiento__seccion-ayuda">
            Estas imágenes fueron marcadas por el equipo como visibles para ti.
          </p>
          <div className="seguimiento__fotografias">
            {servicio.fotografias.map((foto, indice) => (
              <figure className="seguimiento__fotografia" key={`${foto.url}-${indice}`}>
                <img src={foto.url} alt={foto.descripcion || `Evidencia fotográfica ${indice + 1}`} />
                <figcaption>
                  <strong>{foto.tipo}</strong>
                  {foto.descripcion && <span>{foto.descripcion}</span>}
                  <time dateTime={foto.fecha}>{fechaVisible(foto.fecha)}</time>
                </figcaption>
              </figure>
            ))}
          </div>
        </details>
      )}
      {respuesta.isSuccess && (
        <p className="seguimiento__resultado" role="status">
          Tu respuesta fue registrada correctamente.
        </p>
      )}

      {servicio.historial.length > 0 && (
        <section
          className="seguimiento__panel seguimiento__panel--historial"
          aria-labelledby="historial-titulo"
        >
          <h2 id="historial-titulo">Actualizaciones visibles</h2>
          <ul className="seguimiento__historial">
            {servicio.historial.map((registro, indice) => (
              <li key={`${registro.fecha}-${indice}`}>
                <strong>{registro.estado}</strong>
                <span>{registro.comentario || "Sin comentario."}</span>
                <time dateTime={registro.fecha}>
                  {fechaVisible(registro.fecha)}
                </time>
              </li>
            ))}
          </ul>
        </section>
      )}
    </section>
  );
}

export default Seguimiento;
