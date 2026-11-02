import { Link } from "react-router-dom";
import { ArrowLeft, MessageCircle } from "lucide-react";
import Logo from "../components/brand/Logo";
import Seo from "../seo/Seo";
import { urlWhatsApp } from "../config/sitio";
import "./NoEncontrada.css";

const MENSAJE_404 =
  "Hola Hydroemcol, estaba buscando una página en su sitio web y no la encuentro. ¿Me pueden ayudar con esto?";

function NoEncontrada() {
  return (
    <main className="no-encontrada" aria-labelledby="no-encontrada-titulo">
      <Seo
        titulo="Página no encontrada | Hydroemcol S.A.S"
        descripcion="La página que buscas no existe. Comunícate por WhatsApp y te ayudamos a encontrarla o conseguir lo que necesitas."
        noindex
      />
      <div className="no-encontrada__fondo" aria-hidden="true">
        <div className="no-encontrada__rejilla" />
        <div className="no-encontrada__lineas" />
      </div>
      <section className="no-encontrada__tarjeta">
        <header className="no-encontrada__cabecera">
          <Logo grande className="no-encontrada__marca" />
        </header>
        <div className="no-encontrada__cuerpo">
          <p className="no-encontrada__codigo">404</p>
          <p className="no-encontrada__kicker">Error de navegación</p>
          <h1 id="no-encontrada-titulo">La página no fue encontrada</h1>
          <p className="no-encontrada__texto">
            Lo que necesites, comunícate al WhatsApp y lo conseguimos por ti.
          </p>
          <div className="no-encontrada__acciones">
            <a
              className="no-encontrada__boton no-encontrada__boton--whatsapp"
              href={urlWhatsApp(MENSAJE_404)}
              target="_blank"
              rel="noopener noreferrer"
            >
              <MessageCircle size={18} aria-hidden="true" />
              Hablar por WhatsApp
            </a>
            <Link className="no-encontrada__boton" to="/">
              <ArrowLeft size={18} aria-hidden="true" />
              Volver al inicio
            </Link>
          </div>
        </div>
        <footer className="no-encontrada__pie">
          <p>Hydroemcol S.A.S · Sistemas hidráulicos, electrohidráulicos y repuestos</p>
        </footer>
      </section>
    </main>
  );
}

export default NoEncontrada;
