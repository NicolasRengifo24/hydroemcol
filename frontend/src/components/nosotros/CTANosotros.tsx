import { Link } from "react-router-dom";
import { MessageCircle } from "lucide-react";
import { urlWhatsApp } from "../../config/sitio";
import { useAparecerAlEntrar } from "../../hooks/useAparecerAlEntrar";
import "./nosotros.css";

// Sección 7 (y última) de la página Nosotros (RF-1.1): llamado a la acción
// final (RF-7, D-4 aprobada). Banda oscura con título propio coherente con el
// patrón de encabezado del sitio (RF-1.3) y animación de aparición existente
// (RF-9.1).
//
// Jerarquía de acciones (RF-7.1–7.2):
// - Principal: WhatsApp derivado de urlWhatsApp() (config/sitio.ts), sin
//   duplicar el número en este componente. Se abre en pestaña nueva con
//   rel="noopener noreferrer" y aviso para lectores de pantalla (RF-7.3,
//   mismo patrón que CTASection de Inicio).
// - Secundaria: enlace interno a /solicitar con react-router Link (mismo
//   patrón que Inicio), con jerarquía visual diferenciada por las clases
//   __accion--principal / __accion--secundaria de nosotros.css (T3).
//
// Accesibilidad (RNF-5): ambos enlaces son elementos <a> nativos, operables
// con teclado; el foco visible lo define .cta-nosotros__accion:focus-visible
// en nosotros.css. Un único h2 por sección, sin salto de nivel (RNF-3).
//
// Nota (RF-11.1): los textos visibles de esta sección (título y párrafo) son
// PROVISIONALES: no provienen literalmente del folleto aprobado y quedan
// pendientes de validación del cliente. No afirman datos de negocio.

interface CTANosotrosProps {
  id?: string;
}

export function CTANosotros({ id = "cta-nosotros" }: CTANosotrosProps) {
  const { ref, visible } = useAparecerAlEntrar<HTMLElement>();

  return (
    <section
      ref={ref}
      className={`seccion cta-nosotros revelar${visible ? " revelar--visible" : ""}`}
      aria-labelledby={id}
    >
      <span className="cta-nosotros__patron" aria-hidden="true" />
      <h2 className="cta-nosotros__titulo" id={id}>
        {/* PROVISIONAL (RF-11.1): pendiente de validación. */}
        ¿Necesitas asesoría técnica?
      </h2>
      {/* PROVISIONAL (RF-11.1): pendiente de validación. */}
      <p className="cta-nosotros__texto">
        Escríbenos por WhatsApp y recibe atención directa del equipo de Hidroemcol.
      </p>

      <div className="cta-nosotros__acciones">
        <a
          className="cta-nosotros__accion cta-nosotros__accion--principal"
          href={urlWhatsApp()}
          target="_blank"
          rel="noopener noreferrer"
        >
          <MessageCircle size={20} aria-hidden="true" />
          Contactar por WhatsApp
          <span className="sr-only"> (se abre en una pestaña nueva)</span>
        </a>
        <Link
          to="/solicitar"
          className="cta-nosotros__accion cta-nosotros__accion--secundaria"
        >
          Solicitar un servicio
        </Link>
      </div>
    </section>
  );
}
