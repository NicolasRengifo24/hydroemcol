import { SeccionEncabezado } from './SeccionEncabezado'
import { CarruselProductos } from './CarruselProductos'
import { TarjetaServicio } from './TarjetaServicio'
import type { ServicioDestacado } from './contenido'
import { IMAGENES_PRODUCTOS, SERVICIOS_DESTACADOS } from './contenido'
import './inicio.css'

interface BloqueServiciosDestacadosProps {
  servicios?: ServicioDestacado[]
  id?: string
}

export function BloqueServiciosDestacados({
  servicios = SERVICIOS_DESTACADOS,
  id = 'servicios-destacados',
}: BloqueServiciosDestacadosProps) {
  return (
    <section className="seccion seccion--servicios" aria-labelledby={id}>
      <SeccionEncabezado id={id} nivel={2} titulo="Productos y servicios" />
      <div className="rejilla rejilla--destacados">
        {servicios.map((servicio) => (
          servicio.titulo === 'Importación Sobre Pedido' ? (
            <article className="tarjeta tarjeta--destacado tarjeta--importacion" key={servicio.titulo}>
              <h3 className="tarjeta__titulo">{servicio.titulo}</h3>
              <p className="tarjeta__descripcion">{servicio.descripcion}</p>
              <div className="tarjeta__carrusel">
                <CarruselProductos imagenes={IMAGENES_PRODUCTOS} />
              </div>
            </article>
          ) : (
            <TarjetaServicio
              key={servicio.titulo}
              titulo={servicio.titulo}
              descripcion={servicio.descripcion}
              variante="destacado"
            />
          )
        ))}
      </div>
    </section>
  )
}
