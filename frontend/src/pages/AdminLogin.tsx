import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { iniciarSesion } from "../services/api";
import { useDisponibilidadApi } from "../hooks/useDisponibilidadApi";
import { useEsperaProlongada } from "../hooks/useEsperaProlongada";
import Seo from "../seo/Seo";
import AvisoServicio from "../components/AvisoServicio";
import Logo from "../components/brand/Logo";
import { RUTA_ADMIN, RUTA_ADMIN_LOGIN } from "../config/rutasAdmin";

const AVISO_SESION =
  "Tu sesión ha caducado. Vuelve a entrar: tu mensaje seguirá en el campo.";

type EstadoInicioSesion = { from?: unknown; aviso?: unknown };

function estadoInicioSesion(valor: unknown): EstadoInicioSesion | null {
  return typeof valor === "object" && valor !== null
    ? (valor as EstadoInicioSesion)
    : null;
}

function esErrorDeAutenticacion(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    "status" in error &&
    error.status === 401
  );
}

function rutaDeRetornoSegura(valor: unknown): string {
  if (
    typeof valor !== "string" ||
    (valor !== RUTA_ADMIN && !valor.startsWith(`${RUTA_ADMIN}/`)) ||
    valor === RUTA_ADMIN_LOGIN
  ) {
    return RUTA_ADMIN;
  }

  return valor;
}

function AdminLogin() {
  const navigate = useNavigate();
  const location = useLocation();
  const estado = estadoInicioSesion(location.state);
  const [avisoSesion] = useState(
    () => (estado?.aviso === AVISO_SESION ? AVISO_SESION : null),
  );
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const { estado: estadoServicio } = useDisponibilidadApi();
  const sinServicio = estadoServicio === "no_disponible";
  const esperaProlongada = useEsperaProlongada(enviando);

  useEffect(() => {
    if (estado?.aviso !== AVISO_SESION) return;

    // El aviso ya quedó en el estado local; se elimina del router sin perder
    // el destino protegido para conservar el flujo de inicio de sesión.
    navigate(`${location.pathname}${location.search}${location.hash}`, {
      replace: true,
      state: estado.from === undefined ? null : { from: estado.from },
    });
  }, [estado, location.hash, location.pathname, location.search, navigate]);

  async function manejarEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (sinServicio) return;
    setError(null);
    setEnviando(true);

    try {
      await iniciarSesion({ username, password });
      const desde = location.state as { from?: { pathname?: unknown } } | null;
      navigate(rutaDeRetornoSegura(desde?.from?.pathname), { replace: true });
    } catch (errorDeInicio) {
      if (esErrorDeAutenticacion(errorDeInicio)) {
        setError("Usuario o contraseña incorrectos");
      } else {
        setError("No se pudo conectar con el servicio. Intenta nuevamente.");
      }
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section
      className="login-page"
      aria-label="Inicio de sesión administrativo"
    >
      <Seo
        titulo="Acceso administrativo | Hydroemcol S.A.S"
        descripcion="Acceso al panel administrativo de Hydroemcol S.A.S."
        noindex
      />
      <section className="login-card" aria-labelledby="login-titulo">
        <Logo grande className="login-card__brand" />
        <div className="login-card__intro">
          <p className="login-card__eyebrow">Acceso administrativo</p>
          <h1 id="login-titulo">Panel Hydroemcol</h1>
          <p>
            Ingresa con tus credenciales para administrar las solicitudes y
            servicios.
          </p>
        </div>

        {avisoSesion && (
          <p className="login-form__error" role="alert">
            {avisoSesion}
          </p>
        )}

        <form className="login-form" onSubmit={manejarEnvio}>
          <div className="login-form__campo">
            <label htmlFor="username">Usuario</label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(evento) => setUsername(evento.target.value)}
              required
              disabled={enviando || sinServicio}
            />
          </div>

          <div className="login-form__campo">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(evento) => setPassword(evento.target.value)}
              required
              disabled={enviando || sinServicio}
            />
          </div>

          {error && (
            <p className="login-form__error" role="alert">
              {error}
            </p>
          )}

          {sinServicio && (
            <p className="login-form__error" role="status">
              El servicio no está disponible en este momento. El botón se
              habilitará cuando se restablezca.
            </p>
          )}

          {enviando && esperaProlongada && !sinServicio && (
            <p className="login-form__ayuda" role="status">
              El servicio puede tardar hasta un minuto en iniciar…
            </p>
          )}

          <button
            className="login-form__submit"
            type="submit"
            disabled={enviando || sinServicio}
          >
            {enviando ? "Verificando acceso…" : "Ingresar al panel"}
          </button>
        </form>
      </section>
      <AvisoServicio variante="banner" />
    </section>
  );
}

export default AdminLogin;
