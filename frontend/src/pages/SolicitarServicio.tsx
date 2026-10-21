import { useEffect, useRef, useState } from 'react'
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

interface FotoForm {
  id: string
  archivo: File
  url: string
}

interface RespuestaExitosa {
  codigo: string
  enlace: string
}

const CAMPOS_FORM = ['nombre_cliente', 'empresa', 'correo_electronico', 'telefono', 'whatsapp', 'descripcion_problema']

// Fotografías (RF-5): hasta 5 por solicitud, en JPG/JPEG/PNG, 10 MB cada una.
const FOTOS_MAX = 5
const FOTO_TAMANO_MAX = 10 * 1024 * 1024
const FOTO_FORMATOS = ['jpg', 'jpeg', 'png']

function extensionDe(nombre: string): string {
  const punto = nombre.lastIndexOf('.')
  return punto >= 0 ? nombre.slice(punto + 1).toLowerCase() : ''
}

function componenteVacio(): ComponenteForm {
  return { tipo: '', marca: '', referencia: '', descripcion: '', cantidad: 1 }
}

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null
}

function avisoDuplicado(err: unknown): string | null {
  if (!isRecord(err) || err.status !== 409 || !isRecord(err.data)) return null
  if (err.data.requiere_confirmacion !== true) return null
  const detalle = err.data.detail
  return typeof detalle === 'string' && detalle
    ? detalle
    : 'Parece que ya tienes una solicitud en curso.'
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
  const detalle = data.detail
  if (typeof detalle === 'string' && detalle) {
    return { general: detalle, campos }
  }
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
    empresa: '',
    correo_electronico: '',
    telefono: '',
    whatsapp: '',
    descripcion_problema: '',
  })
  const [componentes, setComponentes] = useState<ComponenteForm[]>([componenteVacio()])
  const [fotos, setFotos] = useState<FotoForm[]>([])
  const [errorFotos, setErrorFotos] = useState<string | null>(null)
  const [preferencias, setPreferencias] = useState({
    entregar_en_banco: false,
    avisar_para_coordinar: false,
    recoger: false,
  })
  const [exito, setExito] = useState<RespuestaExitosa | null>(null)
  const [duplicado, setDuplicado] = useState<string | null>(null)
  const [errorCampos, setErrorCampos] = useState<Record<string, string>>({})
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null)
  const [copiado, setCopiado] = useState(false)

  const fotoIdRef = useRef(0)
  const objectUrlsRef = useRef<Set<string>>(new Set())

  useEffect(() => {
    const urls = objectUrlsRef.current
    return () => {
      urls.forEach((url) => URL.revokeObjectURL(url))
      urls.clear()
    }
  }, [])

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

  function onFotosChange(e: React.ChangeEvent<HTMLInputElement>) {
    const seleccionados = Array.from(e.target.files ?? [])
    e.target.value = ''
    if (seleccionados.length === 0) return

    const nuevas: FotoForm[] = []
    let total = fotos.length
    let formatoInvalido = 0
    let tamanoExcedido = 0
    let excedidas = 0

    for (const archivo of seleccionados) {
      if (!FOTO_FORMATOS.includes(extensionDe(archivo.name))) {
        formatoInvalido += 1
        continue
      }
      if (archivo.size > FOTO_TAMANO_MAX) {
        tamanoExcedido += 1
        continue
      }
      if (total >= FOTOS_MAX) {
        excedidas += 1
        continue
      }
      const url = URL.createObjectURL(archivo)
      objectUrlsRef.current.add(url)
      fotoIdRef.current += 1
      nuevas.push({ id: `foto-${fotoIdRef.current}`, archivo, url })
      total += 1
    }

    if (nuevas.length > 0) {
      setFotos((prev) => [...prev, ...nuevas])
    }

    const avisos: string[] = []
    if (formatoInvalido > 0) {
      avisos.push('Solo se aceptan fotografías en formato JPG, JPEG o PNG.')
    }
    if (tamanoExcedido > 0) {
      avisos.push('Cada fotografía debe pesar como máximo 10 MB.')
    }
    if (excedidas > 0) {
      avisos.push(`Máximo ${FOTOS_MAX} fotografías por solicitud.`)
    }
    setErrorFotos(avisos.length > 0 ? avisos.join(' ') : null)
  }

  function quitarFoto(id: string) {
    const foto = fotos.find((f) => f.id === id)
    if (foto) {
      URL.revokeObjectURL(foto.url)
      objectUrlsRef.current.delete(foto.url)
    }
    setFotos((prev) => prev.filter((f) => f.id !== id))
    setErrorFotos(null)
  }

  function alternarPreferencia(campo: keyof typeof preferencias) {
    setPreferencias((prev) => ({ ...prev, [campo]: !prev[campo] }))
  }

  function limpiarErrores() {
    setDuplicado(null)
    setErrorCampos({})
    setErrorGeneral(null)
    setCopiado(false)
  }

  async function enviar(confirmar: boolean) {
    setExito(null)
    limpiarErrores()

    const payload: SolicitudPublicaPayload = {
      nombre_cliente: form.nombre_cliente,
      empresa: form.empresa.trim() || undefined,
      correo_electronico: form.correo_electronico,
      telefono: form.telefono.trim() || undefined,
      whatsapp: form.whatsapp.trim(),
      descripcion_problema: form.descripcion_problema,
      entregar_en_banco: preferencias.entregar_en_banco,
      avisar_para_coordinar: preferencias.avisar_para_coordinar,
      recoger: preferencias.recoger,
      componentes: componentes
        .filter((c) => c.tipo.trim() !== '')
        .map((c) => ({
          tipo: c.tipo,
          marca: c.marca || undefined,
          referencia: c.referencia || undefined,
          descripcion: c.descripcion || undefined,
          cantidad: c.cantidad >= 1 ? c.cantidad : 1,
        })),
      fotografias: fotos.map((f) => f.archivo),
      confirmar,
    }

    try {
      const res = await crear(payload)
      setExito({ codigo: res.codigo, enlace: res.enlace_seguimiento })
    } catch (err) {
      const aviso = avisoDuplicado(err)
      if (aviso) {
        setDuplicado(aviso)
        return
      }
      const { general, campos } = parsearErrores(err)
      setErrorGeneral(general)
      setErrorCampos(campos)
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    void enviar(false)
  }

  function resetearFormulario() {
    objectUrlsRef.current.forEach((url) => URL.revokeObjectURL(url))
    objectUrlsRef.current.clear()
    setForm({
      nombre_cliente: '',
      empresa: '',
      correo_electronico: '',
      telefono: '',
      whatsapp: '',
      descripcion_problema: '',
    })
    setComponentes([componenteVacio()])
    setFotos([])
    setErrorFotos(null)
    setPreferencias({ entregar_en_banco: false, avisar_para_coordinar: false, recoger: false })
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
        No necesitas crear una cuenta para solicitar el servicio. Cuéntanos qué equipo, repuesto o sistema
        necesita atención y un asesor de HidroEmcol se pondrá en contacto contigo por el correo o el teléfono
        que indiques para continuar el proceso.
      </p>

      {exito && (
        <div className="solicitud-panel solicitud-panel-success" role="status" aria-live="polite">
          <p className="solicitud-panel-title">Solicitud creada</p>
          <p>
            Tu solicitud se registró con el código <strong>{exito.codigo}</strong>. El enlace de seguimiento
            da acceso únicamente a esta solicitud y es tu forma de consultar el avance. Guárdalo, junto con el
            código, para volver cuando quieras.
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
          <p className="solicitud-panel-title">Posible solicitud duplicada</p>
          <p>{duplicado}</p>
          <p className="solicitud-panel-actions">
            <button
              type="button"
              className="solicitud-btn solicitud-btn-primary"
              onClick={() => void enviar(true)}
              disabled={isLoading}
            >
              {isLoading ? 'Enviando…' : 'Continuar'}
            </button>
            <button
              type="button"
              className="solicitud-btn solicitud-btn-secondary"
              onClick={() => setDuplicado(null)}
              disabled={isLoading}
            >
              Cancelar
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
                <label className="solicitud-campo-label" htmlFor="f-empresa">
                  Empresa
                </label>
                <input
                  id="f-empresa"
                  className="solicitud-input"
                  type="text"
                  autoComplete="organization"
                  maxLength={200}
                  value={form.empresa}
                  onChange={(e) => actualizarCampo('empresa', e.target.value)}
                />
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
                  Teléfono
                </label>
                <input
                  id="f-telefono"
                  className="solicitud-input"
                  type="tel"
                  autoComplete="tel"
                  inputMode="tel"
                  maxLength={50}
                  aria-invalid={errorCampos.telefono ? 'true' : undefined}
                  aria-describedby={errorCampos.telefono ? 'f-telefono-error' : 'f-contacto-ayuda'}
                  value={form.telefono}
                  onChange={(e) => actualizarCampo('telefono', e.target.value)}
                />
                {errorCampos.telefono && (
                  <p id="f-telefono-error" className="solicitud-error-campo">
                    {errorCampos.telefono}
                  </p>
                )}
              </div>

              <div className="solicitud-campo">
                <label className="solicitud-campo-label" htmlFor="f-whatsapp">
                  WhatsApp
                </label>
                <input
                  id="f-whatsapp"
                  className="solicitud-input"
                  type="tel"
                  inputMode="tel"
                  maxLength={50}
                  required
                  aria-invalid={errorCampos.whatsapp ? 'true' : undefined}
                  aria-describedby={errorCampos.whatsapp ? 'f-whatsapp-error' : 'f-contacto-ayuda'}
                  value={form.whatsapp}
                  onChange={(e) => actualizarCampo('whatsapp', e.target.value)}
                />
                {errorCampos.whatsapp && (
                  <p id="f-whatsapp-error" className="solicitud-error-campo">
                    {errorCampos.whatsapp}
                  </p>
                )}
              </div>

              <p id="f-contacto-ayuda" className="solicitud-ayuda solicitud-grid-full">
                Indica tu número de WhatsApp. Lo usaremos para avisarte del avance de tu servicio.
              </p>
            </div>
          </fieldset>

          <fieldset>
            <legend>Servicio</legend>
            <div className="solicitud-grid">
              <div className="solicitud-campo solicitud-grid-full">
                <label className="solicitud-campo-label" htmlFor="f-descripcion">
                  Descripción del problema <span aria-hidden="true">*</span>
                </label>
                <textarea
                  id="f-descripcion"
                  name="descripcion_problema"
                  rows={4}
                  maxLength={500}
                  required
                  aria-invalid={errorCampos.descripcion_problema ? 'true' : undefined}
                  aria-describedby={
                    errorCampos.descripcion_problema
                      ? 'f-descripcion-error f-descripcion-contador'
                      : 'f-descripcion-contador'
                  }
                  value={form.descripcion_problema}
                  onChange={(e) => actualizarCampo('descripcion_problema', e.target.value)}
                />
                <p id="f-descripcion-contador" className="solicitud-contador">
                  {form.descripcion_problema.length}/500
                </p>
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
            <p className="solicitud-ayuda">
              Agrega un componente por equipo que quieras probar. Puedes quitar cualquiera de ellos
              mientras quede al menos uno.
            </p>
            {componentes.map((c, idx) => (
              <div key={idx} className="solicitud-componente">
                <div className="solicitud-componente-header">
                  <p className="solicitud-componente-titulo">Componente {idx + 1}</p>
                  {componentes.length > 1 && (
                    <button
                      type="button"
                      className="solicitud-btn-ghost"
                      onClick={() => quitarComponente(idx)}
                      aria-label={`Quitar componente ${idx + 1}`}
                    >
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
                  <div className="solicitud-campo solicitud-grid-full">
                    <label className="solicitud-campo-label" htmlFor={`c-${idx}-descripcion`}>
                      Descripción
                    </label>
                    <textarea
                      id={`c-${idx}-descripcion`}
                      className="solicitud-input"
                      rows={2}
                      maxLength={500}
                      value={c.descripcion}
                      onChange={(e) => actualizarComponente(idx, 'descripcion', e.target.value)}
                    />
                    <p className="solicitud-contador">{c.descripcion.length}/500</p>
                  </div>
                </div>
              </div>
            ))}
            <button type="button" className="solicitud-btn solicitud-btn-terciario" onClick={agregarComponente}>
              Agregar componente
            </button>
          </fieldset>

          <fieldset>
            <legend>Fotografías</legend>
            <p className="solicitud-ayuda" id="f-fotos-ayuda">
              Opcional. Puedes adjuntar hasta {FOTOS_MAX} fotografías en formato JPG, JPEG o PNG, de máximo
              10 MB cada una. Ayudan a identificar el estado del componente.
            </p>
            <div className="solicitud-campo">
              <label className="solicitud-campo-label" htmlFor="f-fotos">
                Añadir fotografías
              </label>
              <input
                id="f-fotos"
                className="solicitud-file-input"
                type="file"
                multiple
                accept=".jpg,.jpeg,.png,image/jpeg,image/png"
                aria-describedby={errorFotos ? 'f-fotos-ayuda f-fotos-error' : 'f-fotos-ayuda'}
                aria-invalid={errorFotos ? 'true' : undefined}
                onChange={onFotosChange}
              />
            </div>
            {errorFotos && (
              <p id="f-fotos-error" className="solicitud-error-campo" role="alert">
                {errorFotos}
              </p>
            )}
            <p className="solicitud-contador" aria-live="polite">
              {fotos.length}/{FOTOS_MAX} fotografías adjuntas
            </p>
            {fotos.length > 0 && (
              <ul className="solicitud-fotos" aria-label="Fotografías adjuntas">
                {fotos.map((foto) => (
                  <li key={foto.id} className="solicitud-foto">
                    <img
                      className="solicitud-foto-img"
                      src={foto.url}
                      alt={`Vista previa de ${foto.archivo.name}`}
                    />
                    <div className="solicitud-foto-info">
                      <span className="solicitud-foto-nombre" title={foto.archivo.name}>
                        {foto.archivo.name}
                      </span>
                      <button
                        type="button"
                        className="solicitud-btn-ghost"
                        onClick={() => quitarFoto(foto.id)}
                        aria-label={`Eliminar ${foto.archivo.name}`}
                      >
                        Eliminar
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </fieldset>

          <fieldset>
            <legend>Preferencia de entrega</legend>
            <p className="solicitud-ayuda">Opcional. Puedes marcar una, varias o ninguna.</p>
            <label className="solicitud-check">
              <input
                type="checkbox"
                checked={preferencias.entregar_en_banco}
                onChange={() => alternarPreferencia('entregar_en_banco')}
              />
              <span>Entregar el componente en el banco</span>
            </label>
            <label className="solicitud-check">
              <input
                type="checkbox"
                checked={preferencias.avisar_para_coordinar}
                onChange={() => alternarPreferencia('avisar_para_coordinar')}
              />
              <span>Que me avisen para coordinar la entrega</span>
            </label>
            <label className="solicitud-check">
              <input
                type="checkbox"
                checked={preferencias.recoger}
                onChange={() => alternarPreferencia('recoger')}
              />
              <span>Que recojan el componente</span>
            </label>
          </fieldset>

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
