import { Droplets } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Inicio' },
  { to: '/nosotros', label: 'Nosotros' },
  { to: '/servicios', label: 'Servicios' },
  { to: '/soluciones', label: 'Soluciones' },
  { to: '/contacto', label: 'Contacto' },
  { to: '/solicitar', label: 'Solicitar servicio' },
  { to: '/seguimiento/demo', label: 'Seguimiento' },
]

function Layout() {
  return (
    <div className="layout">
      <header className="header">
        <NavLink to="/" className="brand">
          <Droplets aria-hidden="true" />
          <span>HydroEmcol</span>
        </NavLink>
        <nav className="nav" aria-label="Navegación principal">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="main">
        <Outlet />
      </main>

      <footer className="footer">
        <p>HydroEmcol — sistemas electrohidráulicos</p>
      </footer>
    </div>
  )
}

export default Layout