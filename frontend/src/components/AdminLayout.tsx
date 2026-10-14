import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { cerrarSesion } from '../services/api'

function AdminLayout() {
  const navigate = useNavigate()

  async function manejarCierreSesion() {
    await cerrarSesion()
    navigate('/admin/login', { replace: true })
  }

  return (
    <div className="admin-layout">
      <header className="admin-header">
        <div className="admin-header__marca">
          <span className="admin-header__eyebrow">HIDROEMCOL</span>
          <span className="admin-header__titulo">Operación administrativa</span>
        </div>
        <div className="admin-header__usuario">
          <span className="admin-header__sesion">Sesión administrativa</span>
          <button className="admin-button admin-button--quiet" type="button" onClick={manejarCierreSesion}>
            Cerrar sesión
          </button>
        </div>
      </header>

      <div className="admin-shell">
        <nav className="admin-nav" aria-label="Navegación administrativa">
          <NavLink end to="/admin" className={({ isActive }) => `admin-nav__link${isActive ? ' is-active' : ''}`}>
            Resumen operativo
          </NavLink>
          <NavLink to="/admin/servicios" className={({ isActive }) => `admin-nav__link${isActive ? ' is-active' : ''}`}>
            Servicios
          </NavLink>
        </nav>
        <main className="admin-main">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default AdminLayout
