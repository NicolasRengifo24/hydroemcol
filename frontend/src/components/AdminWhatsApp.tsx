import { useEffect, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useLocation, useNavigate } from 'react-router-dom'
import { useMensajesWhatsapp, useServicioAdministrativo } from '../hooks/useAdministrativo'
import type { MensajeWhatsApp } from '../services/api'
import { abrirWhatsApp, construirUrlWhatsApp } from '../services/whatsapp'

const AVISO_VACIO = 'Escribe el mensaje antes de abrir WhatsApp.'
const AVISO_BLOQUEO = 'El navegador bloqueó la ventana de WhatsApp. Permite las ventanas emergentes para este sitio y pulsa de nuevo el botón.'
const AVISO_ABIERTO = 'Se abrió WhatsApp con el mensaje. Envíalo desde WhatsApp: el sistema no confirma la entrega.'
const AVISO_SESION = 'Tu sesión ha caducado. Vuelve a entrar: tu mensaje seguirá en el campo.'

type CambioPendiente = { componenteId?: number; estado?: string; servicio?: boolean }
type BorradorGuardado = { texto: string; textoVigente: string }

function objeto(valor: unknown): valor is Record<string, unknown> {
  return typeof valor === 'object' && valor !== null
}

function errorEs401(error: unknown): boolean {
  return objeto(error) && error.status === 401
}

function claveBorrador(servicioId: number, clave: string): string {
  return `hidroemcol.whatsapp.${servicioId}.${clave}`
}

function leerBorrador(servicioId: number, clave: string): BorradorGuardado | null {
  try {
    const valor = sessionStorage.getItem(claveBorrador(servicioId, clave))
    if (!valor) return null
    const borrador: unknown = JSON.parse(valor)
    if (!objeto(borrador) || typeof borrador.texto !== 'string' || typeof borrador.textoVigente !== 'string') return null
    return { texto: borrador.texto, textoVigente: borrador.textoVigente }
  } catch {
    return null
  }
}

function guardarBorrador(servicioId: number, mensaje: MensajeWhatsApp, texto: string): void {
  try {
    sessionStorage.setItem(claveBorrador(servicioId, mensaje.clave), JSON.stringify({ texto, textoVigente: mensaje.texto ?? '' }))
  } catch {
    // El almacenamiento puede estar deshabilitado; el editor sigue funcionando en memoria.
  }
}

function borrarBorrador(servicioId: number, clave: string): void {
  try {
    sessionStorage.removeItem(claveBorrador(servicioId, clave))
  } catch {
    // El borrador ya no puede conservarse si el navegador bloquea sessionStorage.
  }
}

function mutacionEsDelServicioActual(
  mutation: { options: { mutationFn?: unknown; meta?: Record<string, unknown> }; state: { variables: unknown; context: unknown } },
  servicioId: number,
  componentes: Array<{ id: number; servicio: number }>,
  cotizaciones: Array<{ id: number }>,
): boolean {
  const meta = mutation.options.meta
  if (meta && (meta.servicioId === servicioId || meta.servicio_id === servicioId)) return true

  const variables = objeto(mutation.state.variables) ? mutation.state.variables : null
  if (variables && (variables.servicioId === servicioId || variables.servicio_id === servicioId)) return true

  if (variables && typeof variables.componenteId === 'number') {
    return componentes.some((componente) => componente.id === variables.componenteId && componente.servicio === servicioId)
  }
  if (variables && typeof variables.id === 'number') {
    return cotizaciones.some((cotizacion) => cotizacion.id === variables.id)
  }

  // Solo se acepta el identificador explícito si la mutación lo expone en sus metadatos
  // o en su función. No se infiere el servicio por el nombre de la mutación.
  return String(mutation.options.mutationFn).includes(`servicioId: ${servicioId}`)
    || String(mutation.options.mutationFn).includes(`servicioId=${servicioId}`)
}

function AdminWhatsApp({ servicioId }: { servicioId: number }) {
  const consulta = useMensajesWhatsapp(servicioId)
  const servicio = useServicioAdministrativo(servicioId)
  const queryClient = useQueryClient()
  const location = useLocation()
  const navigate = useNavigate()
  const [borradores, setBorradores] = useState<Record<string, string>>({})
  const [avisos, setAvisos] = useState<Record<string, string>>({})
  const [sesionCaducada, setSesionCaducada] = useState(false)
  const [recientes, setRecientes] = useState<string[]>([])
  const vigentes = useRef<Record<string, string | null>>({})
  const cambioPendiente = useRef<CambioPendiente | null>(null)
  const aprobacionPendiente = useRef(false)
  const estadosAnteriores = useRef<Record<number, string>>({})
  const servicioActual = useRef(servicio.data)
  const sesionRedirigida = useRef(false)

  useEffect(() => {
    servicioActual.current = servicio.data
  }, [servicio.data])

  useEffect(() => {
    if (sesionRedirigida.current || (!errorEs401(consulta.error) && !errorEs401(servicio.error))) return
    sesionRedirigida.current = true
    setSesionCaducada(true)
    const temporizador = window.setTimeout(() => navigate('/admin/login', {
      replace: true,
      state: { from: location, aviso: AVISO_SESION },
    }), 350)
    return () => window.clearTimeout(temporizador)
  }, [consulta.error, servicio.error, location, navigate])

  useEffect(() => {
    if (!consulta.data) return
    // El borrador solo aplica contra el texto de servidor que estaba vigente al guardarlo.
    // oxlint-disable-next-line react(set-state-in-effect)
    setBorradores((actuales) => {
      const siguientes = { ...actuales }
      consulta.data.mensajes.forEach((mensaje) => {
        const borrador = leerBorrador(servicioId, mensaje.clave)
        if (borrador && borrador.textoVigente === (mensaje.texto ?? '')) {
          siguientes[mensaje.clave] = borrador.texto
        } else {
          siguientes[mensaje.clave] = mensaje.texto ?? ''
          if (borrador) borrarBorrador(servicioId, mensaje.clave)
        }
        vigentes.current[mensaje.clave] = mensaje.texto
      })
      return siguientes
    })
  }, [consulta.data, servicioId])

  // Las mutaciones administrativas ya invalidan las consultas de detalle y WhatsApp.
  // Aquí solo se conserva el evento local que produjo el cambio; nunca se escribe en backend.
  useEffect(() => queryClient.getMutationCache().subscribe((evento) => {
    if (evento.type !== 'updated' || evento.mutation.state.status !== 'success') return
    const variables = evento.mutation.state.variables
    const fuente = String(evento.mutation.options.mutationFn)
    const datosServicio = servicioActual.current
    if (!datosServicio || !mutacionEsDelServicioActual(evento.mutation, servicioId, datosServicio.componentes, datosServicio.cotizaciones)) return
    if (!objeto(variables)) return
    const datos = objeto(variables.datos) ? variables.datos : null
    if (fuente.includes('cambiarEstadoComponente') && typeof variables.componenteId === 'number' && datos && typeof datos.estado === 'string') {
      cambioPendiente.current = { componenteId: variables.componenteId, estado: datos.estado }
    } else if (fuente.includes('registrarRecepcion')) {
      cambioPendiente.current = { servicio: true }
    } else if (fuente.includes('registrarAprobacionExterna')) {
      aprobacionPendiente.current = true
    }
  }), [queryClient, servicioId])

  useEffect(() => {
    const cambio = cambioPendiente.current
    if (!consulta.data || !servicio.data) return
    if (aprobacionPendiente.current && !cambio) {
      const componente = servicio.data.componentes.find((item) => estadosAnteriores.current[item.id] && estadosAnteriores.current[item.id] !== item.estado)
      if (componente) cambioPendiente.current = { componenteId: componente.id, estado: componente.estado }
    }
    const cambioActual = cambioPendiente.current
    if (!cambioActual) {
      servicio.data.componentes.forEach((componente) => { estadosAnteriores.current[componente.id] = componente.estado })
      return
    }
    let clave: string | undefined
    if (cambioActual.servicio) clave = consulta.data.mensajes.find((mensaje) => mensaje.ambito === 'SERVICIO' && mensaje.estado === 'EN_CURSO')?.clave
    if (cambioActual.componenteId !== undefined) {
      const indice = servicio.data.componentes.findIndex((componente) => componente.id === cambioActual.componenteId)
      const estado = servicio.data.componentes[indice]?.estado
      clave = consulta.data.mensajes.find((mensaje) => mensaje.ambito === 'COMPONENTE' && mensaje.clave === `componente-${estado?.toLowerCase()}-${indice}`)?.clave
    }
    if (!clave) return
    // El resaltado sincroniza la tarjeta con la mutación administrativa recién confirmada.
    setTimeout(() => setRecientes((actuales) => actuales.includes(clave as string) ? actuales : [...actuales, clave as string]), 0)
    cambioPendiente.current = null
    aprobacionPendiente.current = false
    servicio.data.componentes.forEach((componente) => { estadosAnteriores.current[componente.id] = componente.estado })
    requestAnimationFrame(() => document.getElementById(`whatsapp-${clave}`)?.focus())
  }, [consulta.data, servicio.data])

  const abrir = (mensaje: MensajeWhatsApp) => {
    const texto = borradores[mensaje.clave] ?? ''
    if (!texto.trim()) {
      setAvisos((actuales) => ({ ...actuales, [mensaje.clave]: AVISO_VACIO }))
      return
    }
    const url = construirUrlWhatsApp(consulta.data?.numero_destino ?? '', texto)
    const abierto = abrirWhatsApp(url)
    if (abierto) borrarBorrador(servicioId, mensaje.clave)
    setAvisos((actuales) => ({ ...actuales, [mensaje.clave]: abierto ? AVISO_ABIERTO : AVISO_BLOQUEO }))
  }

  if (sesionCaducada) return <section className="admin-panel admin-whatsapp" aria-labelledby="whatsapp-titulo"><h2 id="whatsapp-titulo">WhatsApp</h2><p className="admin-feedback admin-feedback--error" role="alert">{AVISO_SESION}</p></section>
  if (consulta.isLoading) return <section className="admin-panel admin-whatsapp" aria-labelledby="whatsapp-titulo"><h2 id="whatsapp-titulo">WhatsApp</h2><p className="admin-feedback" role="status">Preparando mensajes…</p></section>
  if (consulta.isError) return <section className="admin-panel admin-whatsapp" aria-labelledby="whatsapp-titulo"><h2 id="whatsapp-titulo">WhatsApp</h2><div className="admin-feedback admin-feedback--error" role="alert"><p>No se pudo preparar el mensaje. Inténtalo de nuevo.</p><button className="admin-button" type="button" onClick={() => void consulta.refetch()}>Reintentar</button></div></section>
  if (!consulta.data) return null

 return <section className="admin-panel admin-whatsapp" aria-labelledby="whatsapp-titulo"><div className="admin-section-heading"><h2 id="whatsapp-titulo">WhatsApp</h2></div>{consulta.data.aviso && <p className="admin-feedback admin-whatsapp__aviso" role="status">{consulta.data.aviso}</p>}{!consulta.data.aviso && consulta.data.mensajes.length === 0 && <p className="admin-empty">No hay mensajes preparados para este servicio.</p>}<div className="admin-whatsapp__lista">{consulta.data.mensajes.map((mensaje) => { const texto = borradores[mensaje.clave] ?? ''; const idCampo = `whatsapp-${mensaje.clave}`; const idAviso = `${idCampo}-aviso`; const reciente = recientes.includes(mensaje.clave); return <article className={`admin-whatsapp__tarjeta${reciente ? ' admin-whatsapp__tarjeta--reciente' : ''}`} key={mensaje.clave} tabIndex={-1} aria-label={mensaje.etiqueta}>{reciente && <p className="admin-whatsapp__reciente" role="status">Cambio reciente</p>}<div className="admin-whatsapp__encabezado"><div><h3>{mensaje.etiqueta}</h3><p>{mensaje.etiqueta_estado}</p></div><span className="admin-status">{mensaje.estado}</span></div>{mensaje.texto === null ? <p className="admin-feedback admin-feedback--error" role="alert">{mensaje.aviso || 'No se pudo preparar el mensaje. Inténtalo de nuevo.'}</p> : <div className="admin-whatsapp__editor"><label htmlFor={idCampo}>Mensaje para {mensaje.etiqueta}</label><input id={idCampo} type="text" value={texto} aria-invalid={avisos[mensaje.clave] === AVISO_VACIO ? 'true' : undefined} aria-describedby={avisos[mensaje.clave] ? idAviso : undefined} onChange={(event) => { const nuevoTexto = event.target.value; setBorradores((actuales) => ({ ...actuales, [mensaje.clave]: nuevoTexto })); guardarBorrador(servicioId, mensaje, nuevoTexto) }} /><button className="admin-button" type="button" onClick={() => abrir(mensaje)}>Abrir WhatsApp</button>{avisos[mensaje.clave] && <p id={idAviso} className="admin-whatsapp__aviso" role="status">{avisos[mensaje.clave]}</p>}</div>}</article> })}</div></section>
}

export default AdminWhatsApp
