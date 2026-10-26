import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { m } from 'framer-motion'
import { Gauge, Package, Wrench } from 'lucide-react'
import { TarjetaServicio } from './TarjetaServicio'
import { MENSAJE_HERO, TARJETAS_HERO } from './contenido'
import { useRevelar } from '../../hooks/useRevelar'
import './inicio.css'

// Iconos de las tres tarjetas del hero, en el mismo orden que TARJETAS_HERO.
const ICONOS_HERO = [Wrench, Package, Gauge]

interface HeroProps {
  ctaTexto: string
  ctaTo: string
}

// Hero de la página de inicio (RF-2): video de fondo del banco de pruebas, velo de
// color de marca, mensaje principal, llamada a la acción y tres tarjetas de vidrio.
export function Hero({ ctaTexto, ctaTo }: HeroProps) {
  const revelarTexto = useRevelar({ direccion: 'izquierda', distancia: 20 })
  const [reducirMovimiento, setReducirMovimiento] = useState(() =>
    typeof window !== 'undefined'
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
      : false,
  )

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    const actualizarPreferencia = (event: MediaQueryListEvent) => {
      setReducirMovimiento(event.matches)
    }

    mediaQuery.addEventListener('change', actualizarPreferencia)
    return () => mediaQuery.removeEventListener('change', actualizarPreferencia)
  }, [])

  return (
    <section className="hero" aria-labelledby="inicio-hero">
      <video
        className="hero__fondo"
        src="/vid/video-banco-prueba.mp4"
        poster="/img/foto-banco-de-prueba-1.jpeg"
        muted
        loop
        playsInline
        autoPlay={!reducirMovimiento}
        preload="metadata"
        aria-hidden="true"
      />
      <div className="hero__velo" aria-hidden="true" />

      <div className="hero__contenido">
        <m.div className="hero__texto" {...revelarTexto}>
          <p className="hero__eyebrow">Hidroemcol · Ingeniería y servicio técnico</p>
          <h1 id="inicio-hero" className="hero__mensaje">
            {MENSAJE_HERO}
          </h1>
          <Link to={ctaTo} className="hero__cta">
            {ctaTexto}
          </Link>
        </m.div>

        <div className="hero__tarjetas">
          {TARJETAS_HERO.map((tarjeta, i) => (
            <TarjetaServicio
              key={tarjeta.titulo}
              titulo={tarjeta.titulo}
              descripcion={tarjeta.descripcion}
              variante="hero"
              animada
              indice={i}
              nivel={2}
              icono={ICONOS_HERO[i]}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
