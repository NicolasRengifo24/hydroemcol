import { Link } from 'react-router-dom'
import type { LucideIcon } from 'lucide-react'
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
  if (animada) {
    clases.push('tarjeta--animada')
  }

  const className = clases.join(' ')

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

  const estilo =
    animada && indice !== undefined ? { animationDelay: `${indice * 90}ms` } : undefined

  if (to) {
    return (
      <article className={className} style={estilo}>
        <Link to={to} className="tarjeta__enlace">
          {contenido}
        </Link>
      </article>
    )
  }

  return (
    <article className={className} style={estilo}>
      {contenido}
    </article>
  )
}
