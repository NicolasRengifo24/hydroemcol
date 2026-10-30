import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BarChart3,
  ClipboardList,
  LayoutDashboard,
  LogOut,
} from "lucide-react";
import { cerrarSesion } from "../services/api";
import Seo from "../seo/Seo";
import Logo from "./brand/Logo";

function AdminLayout() {
  const navigate = useNavigate();

  async function manejarCierreSesion() {
    await cerrarSesion();
    navigate("/admin/login", { replace: true });
  }

  return (
    <div className="admin-layout">
      <Seo
        titulo="Panel administrativo | Hydroemcol S.A.S"
        descripcion="Acceso al panel administrativo de Hydroemcol S.A.S."
        noindex
      />
      <header className="admin-header">
        <div className="admin-header__marca">
          <Logo mostrarTexto sobreOscuro className="admin-header__logo" />
          <span className="admin-header__titulo">Operación administrativa</span>
        </div>
        <div className="admin-header__usuario">
          <span className="admin-header__sesion">Sesión administrativa</span>
          <button
            className="admin-button admin-button--quiet"
            type="button"
            onClick={manejarCierreSesion}
          >
            <LogOut size={16} aria-hidden="true" />
            Cerrar sesión
          </button>
        </div>
      </header>

      <div className="admin-shell">
        <nav className="admin-nav" aria-label="Navegación administrativa">
          <NavLink
            end
            to="/admin"
            className={({ isActive }) =>
              `admin-nav__link${isActive ? " is-active" : ""}`
            }
          >
            <LayoutDashboard size={18} aria-hidden="true" />
            Resumen operativo
          </NavLink>
          <NavLink
            to="/admin/servicios"
            className={({ isActive }) =>
              `admin-nav__link${isActive ? " is-active" : ""}`
            }
          >
            <ClipboardList size={18} aria-hidden="true" />
            Servicios
          </NavLink>
          <NavLink
            to="/admin/indicadores"
            className={({ isActive }) =>
              `admin-nav__link${isActive ? " is-active" : ""}`
            }
          >
            <BarChart3 size={18} aria-hidden="true" />
            Indicadores
          </NavLink>
        </nav>
        <main className="admin-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AdminLayout;
