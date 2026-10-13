import { useState } from 'react'
import type { FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { iniciarSesion } from '../services/api'

function esErrorDeAutenticacion(error: unknown): boolean {
  return typeof error === 'object' && error !== null && 'status' in error && error.status === 401
}

function rutaDeRetornoSegura(valor: unknown): string {
  if (
    typeof valor !== 'string' ||
    (valor !== '/admin' && !valor.startsWith('/admin/')) ||
    valor === '/admin/login'
  ) {
    return '/admin'
  }

  return valor
}

function AdminLogin() {
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  async function manejarEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError(null)
    setEnviando(true)

    try {
      await iniciarSesion({ username, password })
      const desde = location.state as { from?: { pathname?: unknown } } | null
      navigate(rutaDeRetornoSegura(desde?.from?.pathname), { replace: true })
    } catch (errorDeInicio) {
      if (esErrorDeAutenticacion(errorDeInicio)) {
        setError('Usuario o contraseña incorrectos')
      } else {
        setError('No se pudo conectar con el servicio. Intenta nuevamente.')
      }
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="login-page" aria-label="Inicio de sesión administrativo">
      <section className="login-card" aria-labelledby="login-titulo">
        <div className="login-card__intro">
          <p className="login-card__eyebrow">Acceso administrativo</p>
          <h1 id="login-titulo">Panel Hidroemcol</h1>
          <p>Ingresa con tus credenciales para administrar las solicitudes y servicios.</p>
        </div>

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
              disabled={enviando}
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
              disabled={enviando}
            />
          </div>

          {error && (
            <p className="login-form__error" role="alert">
              {error}
            </p>
          )}

          <button className="login-form__submit" type="submit" disabled={enviando}>
            {enviando ? 'Verificando acceso…' : 'Ingresar al panel'}
          </button>
        </form>
      </section>
    </section>
  )
}

export default AdminLogin
