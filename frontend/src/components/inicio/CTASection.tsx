// Quinta sección de la página de inicio: llamado a la acción final (RF-7, RF-9).
//
// Tres acciones con la jerarquía visual de RF-7.2: "Solicitar un servicio" es
// la acción principal; "Hacer seguimiento" y el contacto son secundarias. El
// contacto usa WhatsApp con alternativa de llamada al mismo número; tanto los
// enlaces como el número visible se derivan del único punto de configuración
// (config/sitio.ts), sin escribir el número a mano (RF-9.2, RF-9.4).
import { Link } from 'react-router-dom'
import { m } from 'framer-motion'
import { MessageCircle, Phone } from 'lucide-react'
import { SeccionEncabezado } from './SeccionEncabezado'
import { urlWhatsApp, urlLlamada, NUMERO_CONTACTO_MOSTRADO } from '../../config/sitio'
import { useRevelar } from '../../hooks/useRevelar'
import './inicio.css'

interface CTASectionProps {
  id?: string
}

export function CTASection({ id = 'cta-final' }: CTASectionProps) {
  const revelarEncabezado = useRevelar()
  const revelarAcciones = useRevelar({ retraso: 0.1 })

  return (
    <section className="seccion seccion--cta" aria-labelledby={id}>
      <span className="cta__patron" aria-hidden="true" />
      <m.div {...revelarEncabezado}>
        <SeccionEncabezado id={id} nivel={2} titulo="Solicita tu servicio" />
      </m.div>
      <m.div className="cta__acciones" {...revelarAcciones}>
        <Link to="/solicitar" className="cta__accion cta__accion--principal">
          Solicitar un servicio
        </Link>
        <Link to="/seguimiento" className="cta__accion cta__accion--secundaria">
          Hacer seguimiento
        </Link>
        <div className="cta__contacto">
          <a
            className="cta__accion cta__accion--secundaria"
            href={urlWhatsApp()}
            target="_blank"
            rel="noopener noreferrer"
          >
            <MessageCircle className="cta__icono" size={20} aria-hidden="true" />
            Escribir por WhatsApp
            <span className="sr-only"> (se abre en una pestaña nueva)</span>
          </a>
          <a className="cta__accion cta__accion--secundaria" href={urlLlamada()}>
            <Phone className="cta__icono" size={20} aria-hidden="true" />
            Llamar al <span className="cta__numero">{NUMERO_CONTACTO_MOSTRADO}</span>
          </a>
        </div>
      </m.div>
    </section>
  )
}
