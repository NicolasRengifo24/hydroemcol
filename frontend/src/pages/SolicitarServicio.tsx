import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCrearSolicitud } from '../hooks/useCrearSolicitud'
import type { SolicitudPublicaPayload } from '../services/solicitudes'
import './SolicitarServicio.css'

interface ComponenteForm {
  tipo: string
  marca: string
  referencia: string
  descripcion: string
  cantidad: number
}

interface RespuestaExitosa {
  codigo: string
  enlace: string
}

const opcionesServicio: ReadonlyArray<{ valor: string; etiqueta: string }> = [
  { valor: 'DIAGNOSTICO', etiqueta: 'Diagnóstico' },
  { valor: 'REPARACION', etiqueta: 'Reparación' },
  { valor: 'MANTENIMIENTO', etiqueta: 'Mantenimiento' },
  { valor: 'PRUEBA', etiqueta: 'Prueba' },
  { valor: 'OTRO', etiqueta: 'Otro' },
]

const CAMPOS_FORM = ['nombre_cliente', 'correo_electronico', 'telefono', 'tipo_servicio', 'descripcion_problema']

function componenteVacio(): ComponenteForm {
  return { tipo: '', marca: '', referencia: '', descripcion: '', cantidad: 1 }
}

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null
}

function esDuplicado(data: unknown): string | null {
  if (!isRecord(data) || !Array.isArray(data.non_field_errors)) return null
  const primero = data.non_field_errors.find((v) => typeof v === 'string')
  if (typeof primero === 'string' && primero.toLowerCase().includes('solicitud en curso')) {
    return primero
  }
  return null
}

function parsearErrores(err: unknown): { general: string | null; campos: Record<string, string> } {
  const campos: Record<string, string> = {}
  const mensajes: string[] = []

  if (!isRecord(err) || !isRecord(err.data)) {
    return {
      general: 'No se pudo enviar la solicitud. Revisa tu conexión e inténtalo de nuevo.',
      campos,
    }
  }

  const data = err.data
  for (const [clave, valor] of Object.entries(data)) {
    if (clave === 'non_field_errors') continue
    if (Array.isArray(valor) && valor.every((v) => typeof v === 'string')) {
      const msg = String(valor[0] ?? '')
      if (CAMPOS_FORM.includes(clave) && msg) {
        campos[clave] = msg
      } else if (msg) {
        mensajes.push(msg)
      }
    } else {
      mensajes.push('Revisa los datos ingresados y vuelve a intentarlo.')
    }
  }

  const general = mensajes[0] ?? (Object.keys(campos).length === 0
    ? 'No se pudo enviar la solicitud. Inténtalo de nuevo.'
    : null)

  return { general, campos }
}

function SolicitarServicio() {
  const { crear, isLoading, reset } = useCrearSolicitud()
  const [form, setForm] = useState({
    nombre_cliente: '',
    correo_electronico: '',
    telefono: '',
    tipo_servicio: 'DIAGNOSTICO',
    descripcion_problema: '',
  })
  const [componentes, setComponentes] = useState<ComponenteForm[]>([componenteVacio()])
  const [exito, setExito] = useState<RespuestaExitosa | null>(null)
  const [duplicado, setDuplicado] = useState<string | null>(null)
  const [errorCampos, setErrorCampos] = useState<Record<string, string>>({})
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null)
  const [copiado, setCopiado] = useState(false)

  function actualizarCampo(campo: keyof typeof form, valor: string) {
    setForm((prev) => ({ ...prev, [campo]: valor }))
  }

  function actualizarComponente(idx: number, campo: keyof ComponenteForm, valor: string | number) {
    setComponentes((prev) => prev.map((c, i) => (i === idx ? { ...c, [campo]: valor } : c)))
  }

  function agregarComponente() {
    setComponentes((prev) => [...prev, componenteVacio()])
  }

  function quitarComponente(idx: number) {
    setComponentes((prev) => prev.filter((_, i) => i !== idx))
  }

  function limpiarErrores() {
    setDuplicado(null)
    setErrorCampos({})
    setErrorGeneral(null)
    setCopiado(false)
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setExito(null)
    limpiarErrores()

    const payload: SolicitudPublicaPayload = {
      nombre_cliente: form.nombre_cliente,
      correo_electronico: form.correo_electronico,
      telefono: form.telefono,
      tipo_servicio: form.tipo_servicio,
      descripcion_problema: form.descripcion_problema,
      componentes: componentes
        .filter((c) => c.tipo.trim() !== '')
        .map((c) => ({
          tipo: c.tipo,
          marca: c.marca || undefined,
          referencia: c.referencia || undefined,
          descripcion: c.descripcion || undefined,
          cantidad: c.cantidad >= 1 ? c.cantidad : 1,
        })),
    }

    try {
      const res = await crear(payload)
      setExito({ codigo: res.codigo, enlace: res.enlace_seguimiento })
    } catch (err) {
      const data = isRecord(err) ? err.data : null
      const mensajeDuplicado = esDuplicado(data)
      if (mensajeDuplicado) {
        setDuplicado(mensajeDuplicado)
        return
      }
      const { general, campos } = parsearErrores(err)
      setErrorGeneral(general)
      setErrorCampos(campos)
    }
  }

  function resetearFormulario() {
    setForm({
      nombre_cliente: '',
      correo_electronico: '',
      telefono: '',
      tipo_servicio: 'DIAGNOSTICO',
      descripcion_problema: '',
    })
    setComponentes([componenteVacio()])
    setExito(null)
    limpiarErrores()
    reset()
  }

  async function copiarEnlace() {
    if (!exito) return
    try {
      await navigator.clipboard.writeText(window.location.origin + exito.enlace)
      setCopiado(true)
    } catch {
      setCopiado(false)
    }
  }

  return (
    <section className="page solicitud-page" aria-label="Solicitar servicio técnico">
      <h1>Solicitar servicio</h1>
      <p className="solicitud-intro">
        Cuéntanos qué equipo, repuesto o sistema necesita atención. Un asesor de HidroEmcol revisará tu
        solicitud y te contactará por el correo o teléfono indicado.
      </p>

      {exito && (
        <div className="solicitud-panel solicitud-panel-success" role="status" aria-live="polite">
          <p className="solicitud-panel-title">Solicitud creada</p>
          <p>
            Tu solicitud se registró con el código <strong>{exito.codigo}</strong>. Guarda este código y el
            siguiente enlace para consultar el estado de tu servicio cuando quieras.
          </p>
          <p className="solicitud-panel-actions">
            <Link to={exito.enlace} className="solicitud-btn solicitud-btn-primary">
              Ver seguimiento de la solicitud
            </Link>
          </p>
          <p className="solicitud-panel-actions">
            <button type="button" className="solicitud-btn solicitud-btn-secondary" onClick={copiarEnlace}>
              {copiado ? 'Enlace copiado' : 'Copiar enlace'}
            </button>
            <button type="button" className="solicitud-btn solicitud-btn-secondary" onClick={resetearFormulario}>
              Solicitar otro servicio
            </button>
          </p>
        </div>
      )}

      {duplicado && (
        <div className="solicitud-panel solicitud-panel-warning" role="alert">
          <p className="solicitud-panel-title">Ya tienes una solicitud en curso</p>
          <p>
            Hay una solicitud activa asociada a tu correo o teléfono y no se permite registrar otra hasta que
            se cierre. Contáctanos por teléfono o correo para reanudarla o darla por finalizada.
          </p>
          <p className="solicitud-panel-actions">
            <button type="button" className="solicitud-btn solicitud-btn-secondary" onClick={() => setDuplicado(null)}>
              Entendido
            </button>
          </p>
        </div>
      )}

      {errorGeneral && !exito && (
        <div className="solicitud-panel solicitud-panel-error" role="alert">
          <p>{errorGeneral}</p>
        </div>
      )}

      {!exito && (
        <form
          onSubmit={onSubmit}
          aria-label="Formulario de solicitud de servicio"
          aria-busy={isLoading}
          className="solicitud-form"
        >
          <fieldset>
            <legend>Datos de contacto</legend>
            <div className="solicitud-grid">
              <div className="solicitud-campo solicitud-grid-full">
                <label className="solicitud-campo-label" htmlFor="f-nombre">
                  Nombre completo <span aria-hidden="true">*</span>
                </label>
                <input
                  id="f-nombre"
                  className="solicitud-input"
                  type="text"
                  autoComplete="name"
                  maxLength={150}
                  required
                  aria-invalid={errorCampos.nombre_cliente ? 'true' : undefined}
                  aria-describedby={errorCampos.nombre_cliente ? 'f-nombre-error' : undefined}
                  value={form.nombre_cliente}
                  onChange={(e) => actualizarCampo('nombre_cliente', e.target.value)}
                />
                {errorCampos.nombre_cliente && (
                  <p id="f-nombre-error" className="solicitud-error-campo">
                    {errorCampos.nombre_cliente}
                  </p>
                )}
              </div>

              <div className="solicitud-campo">
                <label className="solicitud-campo-label" htmlFor="f-correo">
                  Correo electrónico <span aria-hidden="true">*</span>
                </label>
                <input
                  id="f-correo"
                  className="solicitud-input"
                  type="email"
                  autoComplete="email"
                  inputMode="email"
                  maxLength={254}
                  required
                  aria-invalid={errorCampos.correo_electronico ? 'true' : undefined}
                  aria-describedby={errorCampos.correo_electronico ? 'f-correo-error' : undefined}
                  value={form.correo_electronico}
                  onChange={(e) => actualizarCampo('correo_electronico', e.target.value)}
                />
                {errorCampos.correo_electronico && (
                  <p id="f-correo-error" className="solicitud-error-campo">
                    {errorCampos.correo_electronico}
                  </p>
                )}
              </div>

              <div className="solicitud-campo">
                <label className="solicitud-campo-label" htmlFor="f-telefono">
                  Teléfono <span aria-hidden="true">*</span>
                </label>
                <input
                  id="f-telefono"
                  className="solicitud-input"
                  type="tel"
                  autoComplete="tel"
                  inputMode="tel"
                  maxLength={50}
                  required
                  aria-invalid={errorCampos.telefono ? 'true' : undefined}
                  aria-describedby={errorCampos.telefono ? 'f-telefono-error' : undefined}
                  value={form.telefono}
                  onChange={(e) => actualizarCampo('telefono', e.target.value)}
                />
                {errorCampos.telefono && (
                  <p id="f-telefono-error" className="solicitud-error-campo">
                    {errorCampos.telefono}
                  </p>
                )}
              </div>
            </div>
          </fieldset>

          <fieldset>
            <legend>Servicio</legend>
            <div className="solicitud-grid">
              <div className="solicitud-campo solicitud-grid-full">
                <label className="solicitud-campo-label" htmlFor="f-tipo">
                  Tipo de servicio <span aria-hidden="true">*</span>
                </label>
                <select
                  id="f-tipo"
                  name="tipo_servicio"
                  value={form.tipo_servicio}
                  onChange={(e) => actualizarCampo('tipo_servicio', e.target.value)}
                >
                  {opcionesServicio.map((opcion) => (
                    <option key={opcion.valor} value={opcion.valor}>
                      {opcion.etiqueta}
                    </option>
                  ))}
                </select>
              </div>

              <div className="solicitud-campo solicitud-grid-full">
                <label className="solicitud-campo-label" htmlFor="f-descripcion">
                  Descripción del problema <span aria-hidden="true">*</span>
                </label>
                <textarea
                  id="f-descripcion"
                  name="descripcion_problema"
                  rows={4}
                  required
                  aria-invalid={errorCampos.descripcion_problema ? 'true' : undefined}
                  aria-describedby={errorCampos.descripcion_problema ? 'f-descripcion-error' : undefined}
                  value={form.descripcion_problema}
                  onChange={(e) => actualizarCampo('descripcion_problema', e.target.value)}
                />
                {errorCampos.descripcion_problema && (
                  <p id="f-descripcion-error" className="solicitud-error-campo">
                    {errorCampos.descripcion_problema}
                  </p>
                )}
              </div>
            </div>
          </fieldset>

          <fieldset>
            <legend>Componentes</legend>
            {componentes.map((c, idx) => (
              <div key={idx} className="solicitud-componente">
                <div className="solicitud-componente-header">
                  <p className="solicitud-componente-titulo">Componente {idx + 1}</p>
                  {idx > 0 && (
                    <button type="button" className="solicitud-btn-ghost" onClick={() => quitarComponente(idx)}>
                      Quitar
                    </button>
                  )}
                </div>
                <div className="solicitud-grid">
                  <div className="solicitud-campo solicitud-grid-full">
                    <label className="solicitud-campo-label" htmlFor={`c-${idx}-tipo`}>
                      Tipo <span aria-hidden="true">*</span>
                    </label>
                    <input
                      id={`c-${idx}-tipo`}
                      className="solicitud-input"
                      type="text"
                      maxLength={100}
                      required
                      placeholder="Bomba, motor, cilindro, válvula…"
                      value={c.tipo}
                      onChange={(e) => actualizarComponente(idx, 'tipo', e.target.value)}
                    />
                  </div>
                  <div className="solicitud-campo">
                    <label className="solicitud-campo-label" htmlFor={`c-${idx}-cantidad`}>
                      Cantidad
                    </label>
                    <input
                      id={`c-${idx}-cantidad`}
                      className="solicitud-input"
                      type="number"
                      min={1}
                      step={1}
                      value={c.cantidad}
                      onChange={(e) => actualizarComponente(idx, 'cantidad', Number(e.target.value))}
                    />
                  </div>
                  <div className="solicitud-campo">
                    <label className="solicitud-campo-label" htmlFor={`c-${idx}-marca`}>
                      Marca
                    </label>
                    <input
                      id={`c-${idx}-marca`}
                      className="solicitud-input"
                      type="text"
                      maxLength={100}
                      value={c.marca}
                      onChange={(e) => actualizarComponente(idx, 'marca', e.target.value)}
                    />
                  </div>
                  <div className="solicitud-campo">
                    <label className="solicitud-campo-label" htmlFor={`c-${idx}-referencia`}>
                      Referencia
                    </label>
                    <input
                      id={`c-${idx}-referencia`}
                      className="solicitud-input"
                      type="text"
                      maxLength={100}
                      value={c.referencia}
                      onChange={(e) => actualizarComponente(idx, 'referencia', e.target.value)}
                    />
                  </div>
                  <div className="solicitud-campo">
                    <label className="solicitud-campo-label" htmlFor={`c-${idx}-descripcion`}>
                      Descripción
                    </label>
                    <input
                      id={`c-${idx}-descripcion`}
                      className="solicitud-input"
                      type="text"
                      maxLength={255}
                      value={c.descripcion}
                      onChange={(e) => actualizarComponente(idx, 'descripcion', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            ))}
            <button type="button" className="solicitud-btn solicitud-btn-terciario" onClick={agregarComponente}>
              Agregar componente
            </button>
          </fieldset>

          <div className="solicitud-nota" role="note">
            La carga de fotografías de los equipos estará disponible próximamente. Puedes enviarlas por correo o
            WhatsApp después de confirmar la solicitud.
          </div>

          <div className="solicitud-actions">
            <button type="submit" className="solicitud-btn solicitud-btn-primary" disabled={isLoading}>
              {isLoading ? 'Enviando solicitud…' : 'Enviar solicitud'}
            </button>
          </div>
        </form>
      )}
    </section>
  )
}

export default SolicitarServicio