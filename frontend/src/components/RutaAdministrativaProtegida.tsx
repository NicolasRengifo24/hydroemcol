import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useSesion } from '../context/useSesion'

function RutaAdministrativaProtegida() {
  const sesion = useSesion()
  const location = useLocation()

  if (sesion !== 'autenticada') {
    return <Navigate to="/admin/login" replace state={{ from: location }} />
  }

  return <Outlet />
}

export default RutaAdministrativaProtegida
