import { useEffect, useRef, useState } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useSesion } from '../context/useSesion'
import { bootstrapSesion } from '../services/api'
import { RUTA_ADMIN_LOGIN } from '../config/rutasAdmin'

/**
 * Guard de las rutas administrativas (RF-EST-14/15).
 *
 * Al montar sin sesión en memoria intenta restaurarla con `bootstrapSesion()`
 * una sola vez. Mientras el intento está en curso muestra un bloque de carga y
 * **no** redirige; solo cuando termina sin sesión navega al login del panel
 * conservando el destino original en `from`. No se ejecuta en rutas públicas ni
 * en el login porque cuelgan fuera de este componente.
 */
function RutaAdministrativaProtegida() {
  const sesion = useSesion()
  const location = useLocation()
  const bootstrapIniciado = useRef(false)
  const [resolviendo, setResolviendo] = useState(sesion !== 'autenticada')

  useEffect(() => {
    if (bootstrapIniciado.current) return
    bootstrapIniciado.current = true
    if (sesion === 'autenticada') return
    // `bootstrapSesion()` es single-flight: aunque el efecto se repita, no
    // dispara más de una renovación.
    void bootstrapSesion().finally(() => setResolviendo(false))
  }, [sesion])

  if (sesion === 'autenticada') {
    return <Outlet />
  }

  if (resolviendo || sesion === 'autenticando') {
    return (
      <div className="cargando-sesion" role="status">
        Restaurando sesión…
      </div>
    )
  }

  return <Navigate to={RUTA_ADMIN_LOGIN} replace state={{ from: location }} />
}

export default RutaAdministrativaProtegida
