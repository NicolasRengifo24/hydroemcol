import { Link } from 'react-router-dom'
import { Cpu, Package, Wrench } from 'lucide-react'
import { TarjetaServicio } from './TarjetaServicio'
import { MENSAJE_HERO, TARJETAS_HERO } from './contenido'
import './inicio.css'

// Iconos de las tres tarjetas del hero, en el mismo orden que TARJETAS_HERO.
const ICONOS_HERO = [Wrench, Package, Cpu]

interface HeroProps {
  ctaTexto: string
  ctaTo: string
}

// Hero de la página de inicio (RF-2): foto de fondo del banco de pruebas, velo de
// color de marca, mensaje principal, llamada a la acción y tres tarjetas de vidrio.
export function Hero({ ctaTexto, ctaTo }: HeroProps) {
  return (
    <section className="hero" aria-labelledby="inicio-hero">
      <img
        className="hero__fondo"
        src="/img/foto-banco-de-prueba-1.jpeg"
        alt=""
        aria-hidden="true"
        decoding="async"
        fetchPriority="high"
      />
      <div className="hero__velo" aria-hidden="true" />

      <div className="hero__contenido">
        <div className="hero__texto">
          <h1 id="inicio-hero" className="hero__mensaje">
            {MENSAJE_HERO}
          </h1>
          <Link to={ctaTo} className="hero__cta">
            {ctaTexto}
          </Link>
        </div>

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
