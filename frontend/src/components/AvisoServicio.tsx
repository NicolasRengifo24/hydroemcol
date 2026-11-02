import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, RefreshCw, WifiOff } from 'lucide-react'
import { useDisponibilidadApi } from '../hooks/useDisponibilidadApi'
import { comprobarApi } from '../services/disponibilidad'
import './AvisoServicio.css'

const ESPERAS_SONDEO_MS = [10_000, 20_000, 40_000, 60_000]
const DURACION_MAXIMA_SONDEO_MS = 10 * 60 * 1000
const DURACION_MENSAJE_RECUPERADO_MS = 4_000

interface AvisoServicioProps {
  variante?: 'banner' | 'admin'
}

function horaDe(momento: number | null): string | null {
  if (!momento) return null
  return new Intl.DateTimeFormat('es-CO', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(momento))
}

function AvisoServicio({ variante = 'banner' }: AvisoServicioProps) {
  const { estado, ultimaComprobacion } = useDisponibilidadApi()
  const queryClient = useQueryClient()
  const [comprobando, setComprobando] = useState(false)
  const [recuperado, setRecuperado] = useState(false)
  const estadoAnterior = useRef(estado)

  useEffect(() => {
    if (estadoAnterior.current === 'no_disponible' && estado === 'disponible') {
      setRecuperado(true)
      void queryClient.invalidateQueries()
      estadoAnterior.current = estado
      const temporizador = window.setTimeout(
        () => setRecuperado(false),
        DURACION_MENSAJE_RECUPERADO_MS,
      )
      return () => window.clearTimeout(temporizador)
    }
    estadoAnterior.current = estado
  }, [estado, queryClient])

  useEffect(() => {
    if (estado !== 'no_disponible') return

    let cancelado = false
    let indice = 0
    let temporizador: number | undefined
    const inicio = Date.now()

    const programar = () => {
      if (cancelado) return
      if (Date.now() - inicio > DURACION_MAXIMA_SONDEO_MS) return

      const espera =
        ESPERAS_SONDEO_MS[Math.min(indice, ESPERAS_SONDEO_MS.length - 1)]
      indice += 1

      temporizador = window.setTimeout(() => {
        if (cancelado) return
        if (document.visibilityState !== 'visible') return

        void comprobarApi().then(() => {
          if (!cancelado) programar()
        })
      }, espera)
    }

    programar()

    const alCambiarVisibilidad = () => {
      if (document.visibilityState === 'visible') void comprobarApi()
    }
    document.addEventListener('visibilitychange', alCambiarVisibilidad)

    return () => {
      cancelado = true
      if (temporizador !== undefined) window.clearTimeout(temporizador)
      document.removeEventListener('visibilitychange', alCambiarVisibilidad)
    }
  }, [estado])

  const reintentar = async () => {
    if (comprobando) return
    setComprobando(true)
    await comprobarApi()
    setComprobando(false)
  }

  if (recuperado && estado === 'disponible') {
    return (
      <div
        className="aviso-servicio aviso-servicio--exito"
        role="status"
        aria-live="polite"
      >
        <CheckCircle2
          className="aviso-servicio__icono"
          size={20}
          aria-hidden="true"
        />
        <p className="aviso-servicio__titulo">Conexión restablecida.</p>
      </div>
    )
  }

  if (estado !== 'no_disponible') return null

  const hora = horaDe(ultimaComprobacion)

  const contenido = (
    <>
      <div className="aviso-servicio__icono" aria-hidden="true">
        <WifiOff size={22} />
      </div>

      <div className="aviso-servicio__texto">
        <p className="aviso-servicio__titulo">
          Servicio temporalmente fuera de línea
        </p>
        <p className="aviso-servicio__detalle">
          {variante === 'admin'
            ? 'El panel no puede cargar ni guardar datos en este momento. Reintenta en unos instantes.'
            : 'Puedes navegar el sitio, pero el formulario, el seguimiento y el panel no estarán disponibles hasta que se restablezca.'}
        </p>
        <p className="aviso-servicio__pista">
          El servicio puede tardar hasta un minuto en iniciar.
        </p>
        {hora && (
          <p className="aviso-servicio__meta">Última comprobación: {hora}</p>
        )}
      </div>

      <div className="aviso-servicio__acciones">
        <button
          type="button"
          className="aviso-servicio__boton"
          onClick={() => void reintentar()}
          disabled={comprobando}
        >
          <RefreshCw
            size={16}
            aria-hidden="true"
            className={comprobando ? 'aviso-servicio__girando' : undefined}
          />
          {comprobando ? 'Comprobando…' : 'Reintentar'}
        </button>
        {variante === 'admin' && (
          <Link className="aviso-servicio__enlace" to="/">
            Volver al inicio
          </Link>
        )}
      </div>
    </>
  )

  if (variante === 'admin') {
    return (
      <div className="aviso-servicio-fondo">
        <section
          className="aviso-servicio aviso-servicio--admin"
          role="alert"
          aria-live="assertive"
        >
          {contenido}
        </section>
      </div>
    )
  }

  return (
    <div className="aviso-servicio" role="status" aria-live="polite">
      {contenido}
    </div>
  )
}

export default AvisoServicio
