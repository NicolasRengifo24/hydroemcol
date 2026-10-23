// Primera sección de la página Nosotros: hero oscuro (RF-1.1, RF-2, D-1 y D-5).
//
// Sigue el patrón del Hero de Inicio (`components/inicio/Hero.tsx`): imagen
// existente como fondo con velo/sombra oscura encima y texto central encima.
// La imagen es DECORATIVA (RNF-4): queda fuera del árbol de accesibilidad con
// `alt=""` y `aria-hidden="true"`. Si la imagen no carga, la regla base de
// `.hero-nosotros` en nosotros.css conserva el fondo oscuro
// (`--color-primary-deep`) y el mensaje sigue legible sobre el velo (RF-2.3).
//
// El enlace de WhatsApp se deriva de `config/sitio.ts` con `urlWhatsApp()`,
// sin duplicar el número (RF-7.1), y se marca como apertura en pestaña nueva
// con `target="_blank"`, `rel="noopener noreferrer"` y el aviso `sr-only` ya
// usado en el resto del sitio (RF-7.3).
import { MessageCircle } from 'lucide-react'
import {
  HERO_NOSOTROS,
  MENSAJE_HERO_NOSOTROS,
  SUBTITULO_HERO_NOSOTROS,
} from './contenido'
import { urlWhatsApp } from '../../config/sitio'
import './nosotros.css'

// Sección 1: hero oscuro con la imagen `hydroemcol-nosotros.png` (D-5), el
// único `h1` de la página (RNF-3) y el llamado a la acción de WhatsApp (D-4).
// Exportación nombrada, mismo patrón que `components/inicio/`.
export function HeroNosotros() {
  return (
    <section className="hero-nosotros" aria-labelledby="nosotros-hero">
      <img
        className="hero-nosotros__fondo"
        src={HERO_NOSOTROS.src}
        alt=""
        aria-hidden="true"
        decoding="async"
        fetchPriority="high"
      />
      <div className="hero-nosotros__velo" aria-hidden="true" />

      <div className="hero-nosotros__contenido">
        <p className="hero-nosotros__eyebrow">Hydroemcol · Nosotros</p>
        <h1 id="nosotros-hero" className="hero-nosotros__mensaje">
          {MENSAJE_HERO_NOSOTROS}
        </h1>
        <p className="hero-nosotros__texto">{SUBTITULO_HERO_NOSOTROS}</p>
        <a
          className="hero-nosotros__cta"
          href={urlWhatsApp()}
          target="_blank"
          rel="noopener noreferrer"
          style={{ gap: '0.5rem' }}
        >
          <MessageCircle size={20} aria-hidden="true" />
          Contactar por WhatsApp
          <span className="sr-only"> (se abre en una pestaña nueva)</span>
        </a>
      </div>
    </section>
  )
}
