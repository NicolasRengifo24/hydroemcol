import { useState } from 'react'
import { ImageOff } from 'lucide-react'
import type { ProductoVitrina } from '../../services/vitrina'
import { BotonWhatsAppProducto } from './BotonWhatsAppProducto'

interface TarjetaProductoProps {
  producto: ProductoVitrina
}

// Tarjeta de la vitrina (RF-VIT-02). Muestra solo nombre, categoría,
// descripción, imagen con alt y WhatsApp: sin precio, stock ni disponibilidad.
// Si la imagen falla, se oculta la rota y se muestra un marcador con el alt.
export function TarjetaProducto({ producto }: TarjetaProductoProps) {
  const [errorImagen, setErrorImagen] = useState(false)
  const tituloId = `producto-${producto.clave}`

  return (
    <article className="producto-vitrina" aria-labelledby={tituloId}>
      <div className="producto-vitrina__marco">
        {errorImagen ? (
          <div
            className="producto-vitrina__respaldo"
            role="img"
            aria-label={producto.imagen.alt}
          >
            <ImageOff size={28} aria-hidden="true" />
            <span>Imagen no disponible</span>
          </div>
        ) : (
          <img
            className="producto-vitrina__imagen"
            src={producto.imagen.url}
            alt={producto.imagen.alt}
            loading="lazy"
            decoding="async"
            onError={() => setErrorImagen(true)}
          />
        )}
      </div>

      <div className="producto-vitrina__contenido">
        <p className="producto-vitrina__categoria">{producto.categoria.nombre}</p>
        <h3 className="producto-vitrina__titulo" id={tituloId}>
          {producto.nombre}
        </h3>
        <p className="producto-vitrina__descripcion">{producto.descripcion}</p>
        <BotonWhatsAppProducto
          nombre={producto.nombre}
          clave={producto.clave}
          categoria={producto.categoria.slug}
        />
      </div>
    </article>
  )
}
