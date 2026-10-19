import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import "./inicio.css";

interface BloqueVideoProps {
  titulo: string;
  descripcion?: string;
  src?: string; // por defecto '/vid/video-banco-prueba.mp4'
  id?: string;
  poster?: string;
}

export function BloqueVideo({
  titulo,
  descripcion,
  src = "/vid/video-banco-prueba.mp4",
  id,
  poster,
}: BloqueVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  // hayError: el archivo no carga (sustituye todo el bloque por un aviso).
  // avisoReproduccion: el navegador rechazó play(); el video sigue disponible.
  const [hayError, setHayError] = useState(false);
  const [avisoReproduccion, setAvisoReproduccion] = useState(false);
  const [reproduciendo, setReproduciendo] = useState(false);

  const [reducirMovimiento, setReducirMovimiento] = useState(() =>
    typeof window !== "undefined"
      ? window.matchMedia("(prefers-reduced-motion: reduce)").matches
      : false,
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

    const handleChange = (event: MediaQueryListEvent) => {
      setReducirMovimiento(event.matches);
    };

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handleChange);
    } else {
      mediaQuery.addListener(handleChange);
    }

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener("change", handleChange);
      } else {
        mediaQuery.removeListener(handleChange);
      }
    };
  }, []);

  const toggleReproduccion = () => {
    if (!videoRef.current) return;

    if (reproduciendo) {
      videoRef.current.pause();
    } else {
      videoRef.current.play().catch(() => {
        // Un rechazo de play() (política del navegador, pausa rápida) no es un fallo del archivo.
        setAvisoReproduccion(true);
      });
    }
  };

  const handlePlay = () => {
    setAvisoReproduccion(false);
    setReproduciendo(true);
  };

  const handlePause = () => {
    setReproduciendo(false);
  };

  const handleError = () => {
    setHayError(true);
    setReproduciendo(false);
  };

  const handleVideoKeyDown = (event: KeyboardEvent<HTMLVideoElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggleReproduccion();
    }
  };

  if (hayError) {
    return (
      <figure className="video" id={id}>
        <figcaption className="video__titulo">{titulo}</figcaption>
        {descripcion && <p className="video__descripcion">{descripcion}</p>}
        <div className="video__aviso" role="status" aria-live="polite">
          El video del banco de pruebas no está disponible.
        </div>
      </figure>
    );
  }

  return (
    <figure className="video" id={id}>
      <figcaption className="video__titulo">{titulo}</figcaption>
      {descripcion && <p className="video__descripcion">{descripcion}</p>}
      <div className="video__marco">
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
          role="button"
          tabIndex={0}
          aria-label={reproduciendo ? "Pausar video" : "Reproducir video"}
          onClick={toggleReproduccion}
          onKeyDown={handleVideoKeyDown}
          onPlay={handlePlay}
          onPause={handlePause}
          onError={handleError}
        />
      </div>
      {avisoReproduccion && (
        <p className="video__aviso" role="status" aria-live="polite">
          No se pudo iniciar la reproducción. Vuelve a intentarlo.
        </p>
      )}
    </figure>
  );
}
