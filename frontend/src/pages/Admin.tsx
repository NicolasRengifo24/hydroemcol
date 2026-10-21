import { Link } from "react-router-dom";
import { useDashboardAdministrativo } from "../hooks/useAdministrativo";
import type { ServicioResumenAdministrativo } from "../services/api";
import { mensajeDeError } from "../services/errores";

function fechaLegible(fecha: string) {
  return new Intl.DateTimeFormat("es-CO", { dateStyle: "medium" }).format(
    new Date(fecha),
  );
}

function errorLegible(error: unknown) {
  return mensajeDeError(error, "No se pudo cargar el resumen operativo.");
}

function preferenciaEntrega(servicio: ServicioResumenAdministrativo) {
  const preferencias = [
    servicio.entregar_en_banco && "Entregar en banco",
    servicio.avisar_para_coordinar && "Coordinar entrega",
    servicio.recoger && "Recoger componente",
  ].filter(Boolean);
  return preferencias.length ? preferencias.join(" · ") : "Sin preferencia indicada";
}

function ServicioResumen({
  servicio,
}: {
  servicio: ServicioResumenAdministrativo;
}) {
  return (
    <Link className="admin-list-item" to={`/admin/servicios/${servicio.id}`}>
      <span>
        <strong>{servicio.codigo}</strong>
        <small>
          {servicio.cliente.nombre}
          {servicio.cliente.empresa ? ` · ${servicio.cliente.empresa}` : ""}
        </small>
        <small className="admin-list-item__delivery">
          Entrega: {preferenciaEntrega(servicio)}
        </small>
      </span>
      <span className="admin-list-item__meta">
        {servicio.estado}
        <small>{fechaLegible(servicio.fecha_solicitud)}</small>
      </span>
    </Link>
  );
}

function Admin() {
  const consulta = useDashboardAdministrativo();

  return (
    <section className="admin-page" aria-labelledby="dashboard-titulo">
      <div className="admin-page__intro">
        <div>
          <p className="admin-kicker">Control de operación</p>
          <h1 id="dashboard-titulo">Resumen operativo</h1>
          <p className="admin-lead">
            Una lectura rápida de los servicios que requieren seguimiento
            técnico y administrativo.
          </p>
        </div>
        <Link className="admin-button" to="/admin/servicios">
          Ver todos los servicios
        </Link>
      </div>
      {consulta.isLoading && (
        <p className="admin-feedback" role="status">
          Cargando resumen operativo…
        </p>
      )}
      {consulta.isError && (
        <div className="admin-feedback admin-feedback--error" role="alert">
          <p>{errorLegible(consulta.error)}</p>
          <button
            className="admin-button"
            type="button"
            onClick={() => void consulta.refetch()}
          >
            Reintentar
          </button>
        </div>
      )}
      {consulta.isSuccess && (
        <>
          <section className="admin-overview" aria-labelledby="lectura-titulo">
            <div className="admin-section-heading">
              <div>
                <p className="admin-kicker">Lectura rápida</p>
                <h2 id="lectura-titulo">Estado de la operación</h2>
              </div>
              <span className="admin-section-note">Datos en tiempo real</span>
            </div>
            <div className="admin-metrics admin-metrics--overview">
              <Link className="admin-metric admin-metric--total" to="/admin/servicios">
                <span>Servicios activos</span>
                <strong>{consulta.data.total_activos}</strong>
                <small>Ver cartera completa</small>
              </Link>
              <Link className="admin-metric" to="/admin/servicios?estado=SOLICITADO">
                <span>Nuevas solicitudes</span>
                <strong>{consulta.data.contadores.SOLICITADO ?? 0}</strong>
                <small>Requieren primera revisión</small>
              </Link>
              <Link className="admin-metric" to="/admin/servicios?estado=EN_CURSO">
                <span>En curso</span>
                <strong>{consulta.data.contadores.EN_CURSO ?? 0}</strong>
                <small>Atención actualmente activa</small>
              </Link>
              <Link className="admin-metric admin-metric--attention" to="/admin/servicios">
                <span>Prioridad de atención</span>
                <strong>{consulta.data.pendientes_atencion.length}</strong>
                <small>Casos que necesitan seguimiento</small>
              </Link>
            </div>
          </section>
          <div className="admin-dashboard-grid">
            <section className="admin-panel" aria-labelledby="recientes-titulo">
              <div className="admin-section-heading">
                <h2 id="recientes-titulo">Servicios recientes</h2>
                <span>Últimos 10</span>
              </div>
              {consulta.data.recientes.length ? (
                <div className="admin-list">
                  {consulta.data.recientes.map((servicio) => (
                    <ServicioResumen key={servicio.id} servicio={servicio} />
                  ))}
                </div>
              ) : (
                <p className="admin-muted">
                  No hay servicios activos recientes.
                </p>
              )}
            </section>
            <section
              className="admin-panel"
              aria-labelledby="pendientes-titulo"
            >
              <div className="admin-section-heading">
                <h2 id="pendientes-titulo">Pendientes de atención</h2>
                <span>Prioridad operativa</span>
              </div>
              {consulta.data.pendientes_atencion.length ? (
                <div className="admin-list">
                  {consulta.data.pendientes_atencion.map((servicio) => (
                    <ServicioResumen key={servicio.id} servicio={servicio} />
                  ))}
                </div>
              ) : (
                <p className="admin-muted">
                  No hay servicios pendientes de atención.
                </p>
              )}
            </section>
          </div>
        </>
      )}
    </section>
  );
}

export default Admin;
