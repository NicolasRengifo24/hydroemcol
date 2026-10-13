import { useEffect, useRef, useState } from 'react'
import { Play, Pause } from 'lucide-react'
import './inicio.css'

interface BloqueVideoProps {
  titulo: string
  descripcion?: string
  src?: string // por defecto '/vid/video-banco-prueba.mp4'
  id?: string
  poster?: string
}

export function BloqueVideo({
  titulo,
  descripcion,
  src = '/vid/video-banco-prueba.mp4',
  id,
  poster,
}: BloqueVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [hayError, setHayError] = useState(false)
  const [reproduciendo, setReproduciendo] = useState(false)

  const [reducirMovimiento, setReducirMovimiento] = useState(() =>
    typeof window !== 'undefined' ? window.matchMedia('(prefers-reduced-motion: reduce)').matches : false
  )

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')

    const handleChange = (event: MediaQueryListEvent) => {
      setReducirMovimiento(event.matches)
    }

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange)
    } else {
      mediaQuery.addListener(handleChange)
    }

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange)
      } else {
        mediaQuery.removeListener(handleChange)
      }
    }
  }, [])

  const toggleReproduccion = () => {
    if (!videoRef.current) return

    if (reproduciendo) {
      videoRef.current.pause()
    } else {
      videoRef.current.play().catch(() => {
        // Ignorar errores de reproducción automática (p.ej. políticas del navegador)
        setHayError(true)
      })
    }
  }

  const handlePlay = () => {
    setReproduciendo(true)
  }

  const handlePause = () => {
    setReproduciendo(false)
  }

  const handleError = () => {
    setHayError(true)
    setReproduciendo(false)
  }

  if (hayError) {
    return (
      <figure className="video" id={id}>
        <figcaption className="video__titulo">{titulo}</figcaption>
        {descripcion && <p className="video__descripcion">{descripcion}</p>}
        <div className="video__aviso" role="status" aria-live="polite">
          El video del banco de pruebas no está disponible.
        </div>
      </figure>
    )
  }

  return (
    <figure className="video" id={id}>
      <figcaption className="video__titulo">{titulo}</figcaption>
      {descripcion && <p className="video__descripcion">{descripcion}</p>}
      <video
        ref={videoRef}
        className="video__elemento"
        muted
        loop
        playsInline
        preload="metadata"
        poster={poster}
        autoPlay={!reducirMovimiento}
        src={src}
        onPlay={handlePlay}
        onPause={handlePause}
        onError={handleError}
      />
      <button
        type="button"
        className="video__control"
        onClick={toggleReproduccion}
        aria-pressed={reproduciendo}
      >
        {reproduciendo ? <Pause size={20} aria-hidden="true" /> : <Play size={20} aria-hidden="true" />}
        <span className="video__control-text">
          {reproduciendo ? 'Pausar video' : 'Reproducir video'}
        </span>
      </button>
    </figure>
  )
}
