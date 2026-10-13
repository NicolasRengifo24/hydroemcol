import { Link } from 'react-router-dom'
import { TarjetaServicio } from './TarjetaServicio'
import { MENSAJE_HERO, TARJETAS_HERO } from './contenido'
import './inicio.css'

interface HeroProps {
  ctaTexto: string
  ctaTo: string
}

export function Hero({ ctaTexto, ctaTo }: HeroProps) {
  return (
    <section className="hero" aria-labelledby="inicio-hero">
      <h1 id="inicio-hero" className="hero__mensaje">
        {MENSAJE_HERO}
      </h1>

      <Link to={ctaTo} className="hero__cta">
        {ctaTexto}
      </Link>

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
          />
        ))}
      </div>
    </section>
  )
}
