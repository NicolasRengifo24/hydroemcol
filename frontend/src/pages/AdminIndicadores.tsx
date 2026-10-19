import { Link } from "react-router-dom";
import { useDashboardAdministrativo } from "../hooks/useAdministrativo";
import type { CodigoEstadoServicio } from "../services/api";

const estados: Array<{ codigo: CodigoEstadoServicio; etiqueta: string }> = [
  { codigo: "SOLICITADO", etiqueta: "Solicitados" },
  { codigo: "EN_CURSO", etiqueta: "En curso" },
  { codigo: "FINALIZADO", etiqueta: "Finalizados" },
  { codigo: "CANCELADO", etiqueta: "Cancelados" },
];

function errorLegible(error: unknown) {
  if (typeof error === "object" && error !== null && "data" in error) {
    const data = (error as { data?: { detail?: string } }).data;
    if (data?.detail) return data.detail;
  }
  return "No se pudieron cargar los indicadores operativos.";
}

function GraficaEstados({
  contadores,
}: {
  contadores: Record<string, number>;
}) {
  const valores = estados.map((estado) => contadores[estado.codigo] ?? 0);
  const maximo = Math.max(...valores, 1);

  return (
    <div
      className="admin-status-chart"
      role="list"
      aria-label="Servicios activos por estado"
    >
      {estados.map((estado) => {
        const valor = contadores[estado.codigo] ?? 0;
        const porcentaje = Math.max((valor / maximo) * 100, valor > 0 ? 8 : 0);
        return (
          <Link
            key={estado.codigo}
            to={`/admin/servicios?estado=${estado.codigo}`}
            className="admin-status-chart__row"
            role="listitem"
          >
            <span className="admin-status-chart__label">{estado.etiqueta}</span>
            <span className="admin-status-chart__track" aria-hidden="true">
              <span
                className="admin-status-chart__bar"
                style={{ width: `${porcentaje}%` }}
              />
            </span>
            <strong>{valor}</strong>
          </Link>
        );
      })}
    </div>
  );
}

function AdminIndicadores() {
  const consulta = useDashboardAdministrativo();

  return (
    <section className="admin-page" aria-labelledby="indicadores-titulo">
      <div className="admin-page__intro">
        <div>
          <p className="admin-kicker">Lectura de operación</p>
          <h1 id="indicadores-titulo">Indicadores</h1>
          <p className="admin-lead">
            Distribución actual de los servicios y carga prioritaria de
            atención.
          </p>
        </div>
        <Link className="admin-button" to="/admin/servicios">
          Ver servicios
        </Link>
      </div>

      {consulta.isLoading && (
        <p className="admin-feedback" role="status">
          Cargando indicadores operativos…
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
          <section
            className="admin-insights"
            aria-labelledby="indicadores-activos-titulo"
          >
            <div className="admin-section-heading">
              <div>
                <p className="admin-kicker">Datos del servidor</p>
                <h2 id="indicadores-activos-titulo">Indicadores activos</h2>
              </div>
              <span className="admin-section-note">Solo servicios activos</span>
            </div>
            <div className="admin-metrics">
              <Link
                className="admin-metric admin-metric--total"
                to="/admin/servicios"
              >
                <span>Total activos</span>
                <strong>{consulta.data.total_activos}</strong>
              </Link>
              {estados.slice(0, 4).map((estado) => (
                <Link
                  className="admin-metric"
                  key={estado.codigo}
                  to={`/admin/servicios?estado=${estado.codigo}`}
                >
                  <span>{estado.etiqueta}</span>
                  <strong>
                    {consulta.data.contadores[estado.codigo] ?? 0}
                  </strong>
                </Link>
              ))}
            </div>
          </section>

          <div className="admin-insights-grid">
            <section
              className="admin-panel admin-panel--chart"
              aria-labelledby="grafica-estados-titulo"
            >
              <div className="admin-section-heading">
                <h2 id="grafica-estados-titulo">Servicios por estado</h2>
                <span>Distribución actual</span>
              </div>
              <GraficaEstados contadores={consulta.data.contadores} />
            </section>
            <section
              className="admin-panel admin-panel--workload"
              aria-labelledby="carga-titulo"
            >
              <div className="admin-section-heading">
                <h2 id="carga-titulo">Carga operativa</h2>
                <span>Prioridad de atención</span>
              </div>
              <div className="admin-workload">
                <div>
                  <span>Pendientes</span>
                  <strong>{consulta.data.pendientes_atencion.length}</strong>
                </div>
                <div>
                  <span>Esperando aprobación</span>
                  <strong>
                    {consulta.data.contadores.ESPERANDO_APROBACION ?? 0}
                  </strong>
                </div>
                <div>
                  <span>En pruebas</span>
                  <strong>{consulta.data.contadores.EN_PRUEBAS ?? 0}</strong>
                </div>
              </div>
            </section>
          </div>
        </>
      )}
    </section>
  );
}

export default AdminIndicadores;
