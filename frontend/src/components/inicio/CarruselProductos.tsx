import { useState } from 'react'
import type { ImagenFolleto } from './contenido'
import './inicio.css'

interface CarruselProductosProps {
  imagenes: ImagenFolleto[]
  ariaLabel?: string
}

export function CarruselProductos({
  imagenes,
  ariaLabel = 'Carrusel de productos de importación',
}: CarruselProductosProps) {
  const [indiceActivo, setIndiceActivo] = useState(0)
  const [hayError, setHayError] = useState(false)
  const indiceVisible = Math.min(indiceActivo, Math.max(imagenes.length - 1, 0))
  const imagenActiva = imagenes[indiceVisible]
  const hayImagenes = imagenes.length > 0
  const esPrimeraImagen = indiceVisible === 0
  const esUltimaImagen = indiceVisible === imagenes.length - 1

  const cambiarImagen = (nuevoIndice: number) => {
    setIndiceActivo(nuevoIndice)
    setHayError(false)
  }

  const mostrarAnterior = () => {
    if (!esPrimeraImagen) cambiarImagen(indiceVisible - 1)
  }

  const mostrarSiguiente = () => {
    if (!esUltimaImagen) cambiarImagen(indiceVisible + 1)
  }

  return (
    <div className="carrusel" role="group" aria-label={ariaLabel}>
      <div className="carrusel__marco">
        {imagenActiva && !hayError ? (
          <img
            className="carrusel__imagen"
            src={imagenActiva.src}
            alt={imagenActiva.alt}
            onError={() => setHayError(true)}
          />
        ) : (
          <p className="carrusel__error" role="status">
            {hayImagenes
              ? 'Esta imagen no está disponible. Puedes continuar con las demás imágenes.'
              : 'No hay imágenes de productos disponibles.'}
          </p>
        )}
      </div>

      <div className="carrusel__controles">
        <button
          type="button"
          className="carrusel__control"
          onClick={mostrarAnterior}
          disabled={!hayImagenes || esPrimeraImagen}
          aria-label="Mostrar imagen anterior"
        >
          Anterior
        </button>
        <button
          type="button"
          className="carrusel__control"
          onClick={mostrarSiguiente}
          disabled={!hayImagenes || esUltimaImagen}
          aria-label="Mostrar imagen siguiente"
        >
          Siguiente
        </button>
      </div>

      <p className="carrusel__posicion" aria-live="polite" aria-atomic="true">
        {hayImagenes ? `Imagen ${indiceVisible + 1} de ${imagenes.length}` : 'Carrusel sin imágenes'}
      </p>
    </div>
  )
}
