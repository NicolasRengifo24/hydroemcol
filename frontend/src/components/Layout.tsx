import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { Menu, MessageCircle, Phone, X } from "lucide-react";
import Logo from "./brand/Logo";
import Seo from "../seo/Seo";
import {
  NUMERO_CONTACTO_MOSTRADO,
  URL_FACEBOOK,
  urlLlamada,
  urlWhatsApp,
} from "../config/sitio";

const ANIO_ACTUAL = new Date().getFullYear();

const navItems = [
  { to: "/", label: "Inicio" },
  { to: "/soluciones", label: "Soluciones" },
  { to: "/solicitar", label: "Solicitar servicio" },
  { to: "/seguimiento", label: "Seguimiento" },
  { to: "/nosotros", label: "Nosotros" },
];

function Layout() {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [encabezadoEnScroll, setEncabezadoEnScroll] = useState(false);

  // Con el menú móvil abierto, Escape lo cierra (teclado, RNF-6).
  useEffect(() => {
    if (!menuAbierto) return;

    const alPulsarTecla = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") setMenuAbierto(false);
    };
    window.addEventListener("keydown", alPulsarTecla);
    return () => window.removeEventListener("keydown", alPulsarTecla);
  }, [menuAbierto]);

  // El encabezado cambia a fondo oscuro cuando la página ha recorrido un poco.
  useEffect(() => {
    const alDesplazar = () => setEncabezadoEnScroll(window.scrollY > 8);
    alDesplazar();
    window.addEventListener("scroll", alDesplazar, { passive: true });
    return () => window.removeEventListener("scroll", alDesplazar);
  }, []);

  const cerrarMenu = () => setMenuAbierto(false);

  return (
    <div className="layout">
      <Seo />
      <header
        className={encabezadoEnScroll ? "header header--scrolled" : "header"}
      >
        <div className="header__fila">
          <NavLink
            to="/"
            className="brand"
            aria-label="Hydroemcol S.A.S - inicio"
            onClick={cerrarMenu}
          >
            <Logo sobreOscuro />
          </NavLink>

          <nav
            id="menu-principal"
            className={menuAbierto ? "nav nav--abierto" : "nav"}
            aria-label="Navegación principal"
          >
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={cerrarMenu}
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="header__acciones">
            <a
              className="header__whatsapp"
              href={urlWhatsApp()}
              target="_blank"
              rel="noopener noreferrer"
            >
              <MessageCircle size={20} aria-hidden="true" />
              <span className="header__whatsapp-texto">WhatsApp</span>
              <span className="sr-only">(se abre en una pestaña nueva)</span>
            </a>

            <button
              type="button"
              className="header__menu"
              aria-expanded={menuAbierto}
              aria-controls="menu-principal"
              onClick={() => setMenuAbierto((abierto) => !abierto)}
            >
              {menuAbierto ? (
                <X size={20} aria-hidden="true" />
              ) : (
                <Menu size={20} aria-hidden="true" />
              )}
              <span>{menuAbierto ? "Cerrar" : "Menú"}</span>
            </button>
          </div>
        </div>
      </header>

      <main className="main">
        <Outlet />
      </main>

      <footer className="footer">
        <div className="footer__columnas">
          <div className="footer__bloque">
            <Logo sobreOscuro />
            <p className="footer__marca">Hydroemcol S.A.S</p>
            <p className="footer__descripcion">
              Sistemas hidráulicos y electrohidráulicos: servicio técnico,
              repuestos e importación sobre pedido.
            </p>
          </div>

          <div className="footer__bloque">
            <h2 className="footer__titulo">Contacto</h2>
            <ul className="footer__contacto">
              <li>
                <a
                  href={urlWhatsApp()}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <MessageCircle size={18} aria-hidden="true" />
                  WhatsApp
                  <span className="sr-only">
                    {" "}
                    (se abre en una pestaña nueva)
                  </span>
                </a>
              </li>
              <li>
                <a href={urlLlamada()}>
                  <Phone size={18} aria-hidden="true" />
                  Llamar {NUMERO_CONTACTO_MOSTRADO}
                </a>
              </li>
            </ul>
          </div>

          <div className="footer__bloque">
            <h2 className="footer__titulo">Síguenos</h2>
            <ul className="footer__contacto">
              <li>
                <a
                  className="footer__facebook"
                  href={URL_FACEBOOK}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Facebook
                  <span className="sr-only">
                    {" "}
                    (se abre en una pestaña nueva)
                  </span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <p className="footer__copyright">© {ANIO_ACTUAL} Hydroemcol S.A.S.</p>
      </footer>
    </div>
  );
}

export default Layout;
