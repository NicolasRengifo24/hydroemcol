import { Link } from 'react-router-dom'
import { m } from 'framer-motion'
import type { LucideIcon } from 'lucide-react'
import { useRevelar } from '../../hooks/useRevelar'
import './inicio.css'

interface TarjetaServicioProps {
  titulo: string
  descripcion: string
  animada?: boolean               // por defecto false
  indice?: number                 // retardo de la animación escalonada
  variante?: 'hero' | 'destacado' // por defecto 'hero'
  to?: string                     // OPCIONAL: si se indica, la tarjeta se renderiza como enlace (interactiva, con elevación); si no, es informativa (RF-3.3)
  nivel?: 2 | 3                   // por defecto 3; el hero pasa 2 para no saltar niveles tras el h1 (RNF-4)
  icono?: LucideIcon              // icono decorativo (aria-hidden)
  claseExtra?: string             // clase opcional para variantes de presentación
}

export function TarjetaServicio({
  titulo,
  descripcion,
  animada = false,
  indice,
  variante = 'hero',
  to,
  nivel = 3,
  icono: Icono,
  claseExtra,
}: TarjetaServicioProps) {
  const clases = ['tarjeta']
  if (variante === 'hero') {
    clases.push('tarjeta--hero')
  } else {
    clases.push('tarjeta--destacado')
  }
  if (to) {
    clases.push('tarjeta--interactiva')
  }
  if (claseExtra) {
    clases.push(claseExtra)
  }

  const className = clases.join(' ')
  const revelar = useRevelar({
    direccion: 'arriba',
    retraso: (indice ?? 0) * 0.07,
  })

  const Encabezado = nivel === 2 ? 'h2' : 'h3'

  const contenido = (
    <>
      {Icono && (
        <span className="tarjeta__icono" aria-hidden="true">
          <Icono size={22} strokeWidth={1.9} />
        </span>
      )}
      <Encabezado className="tarjeta__titulo">{titulo}</Encabezado>
      <p className="tarjeta__descripcion">{descripcion}</p>
    </>
  )

  const movimiento = animada ? revelar : {}

  if (to) {
    return (
      <m.article className={className} {...movimiento}>
        <Link to={to} className="tarjeta__enlace">
          {contenido}
        </Link>
      </m.article>
    )
  }

  return (
    <m.article className={className} {...movimiento}>
      {contenido}
    </m.article>
  )
}
