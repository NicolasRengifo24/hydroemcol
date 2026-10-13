import { NavLink, Outlet } from 'react-router-dom'
import Logo from './brand/Logo'
import { URL_FACEBOOK } from '../config/sitio'

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
        <NavLink to="/" className="brand" aria-label="Hidroemcol - inicio">
          <Logo />
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
        <a
          className="footer__facebook"
          href={URL_FACEBOOK}
          target="_blank"
          rel="noopener noreferrer"
        >
          Facebook
        </a>
      </footer>
    </div>
  )
}

export default Layout