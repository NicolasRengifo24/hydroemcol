import { useState } from 'react'
import { MessageCircle } from 'lucide-react'
import { urlWhatsAppProducto } from '../../config/sitio'
import { enviarContactoProducto } from '../../services/medicion'

interface BotonWhatsAppProductoProps {
  nombre: string
  clave: string
  categoria: string
}

// Enlace de WhatsApp por producto (RF-VIT-23/24). El número es el central de
// `config/sitio.ts`; el mensaje solo sustituye el nombre. El aviso informa que
// se abrió WhatsApp, sin afirmar que el mensaje se envió o la conversación
// comenzó.
export function BotonWhatsAppProducto({
  nombre,
  clave,
  categoria,
}: BotonWhatsAppProductoProps) {
  const [avisoVisible, setAvisoVisible] = useState(false)

  return (
    <div className="producto-vitrina__contacto">
      <a
        className="producto-vitrina__whatsapp"
        href={urlWhatsAppProducto(nombre)}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`Consultar por WhatsApp sobre ${nombre} (se abre en una pestaña nueva)`}
        onClick={() => {
          setAvisoVisible(true)
          enviarContactoProducto({ clave, categoria })
        }}
      >
        <MessageCircle size={19} aria-hidden="true" />
        Consultar por WhatsApp
      </a>
      <p className="producto-vitrina__aviso" role="status">
        {avisoVisible
          ? 'Se abrió WhatsApp en otra pestaña. El mensaje se envía desde la aplicación.'
          : ''}
      </p>
    </div>
  )
}
