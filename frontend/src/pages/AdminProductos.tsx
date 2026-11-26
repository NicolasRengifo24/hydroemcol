import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { Eye, EyeOff, ImageOff, Pencil, Plus, Trash } from 'lucide-react'
import { AdminConfirmDialog } from '../components/AdminConfirmDialog'
import { useMutacionesProductos, useProductosAdministrativos } from '../hooks/useAdministrativo'
import { useVitrina } from '../hooks/useVitrina'
import { mensajeDeError } from '../services/errores'
import type { ProductoAdministrativo } from '../services/vitrina'
import './adminVitrina.css'

const LIMITE_IMAGEN = 5 * 1024 * 1024
const TIPOS_IMAGEN = ['image/jpeg', 'image/png', 'image/webp']

type Borrador = {
  id?: number
  nombre: string
  categoria: string
  descripcion: string
  imagenAlt: string
  visible: boolean
}

function fechaLegible(fecha: string) {
  return new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(fecha))
}

function validarImagen(archivo: File | null): string {
  if (!archivo) return ''
  if (!TIPOS_IMAGEN.includes(archivo.type)) {
    return 'Usa una imagen JPG, PNG o WEBP.'
  }
  if (archivo.size > LIMITE_IMAGEN) {
    return 'La imagen supera los 5 MB.'
  }
  return ''
}

function erroresDeCampo(error: unknown): Record<string, string> {
  if (typeof error !== 'object' || error === null || !('data' in error)) return {}
  const datos = (error as { data?: unknown }).data
  if (typeof datos !== 'object' || datos === null || Array.isArray(datos)) return {}

  const resultado: Record<string, string> = {}
  for (const [campo, valor] of Object.entries(datos)) {
    if (campo === 'detail' || campo === 'motivo') continue
    const texto = Array.isArray(valor)
      ? valor.find((item): item is string => typeof item === 'string')
      : typeof valor === 'string'
        ? valor
        : undefined
    if (texto) resultado[campo] = texto
  }
  return resultado
}

function ErrorCampo({ id, mensaje }: { id: string; mensaje?: string }) {
  if (!mensaje) return null
  return (
    <p className="admin-vitrina-error-campo" id={id} role="alert">
      {mensaje}
    </p>
  )
}

function AdminProductos() {
  const consulta = useProductosAdministrativos()
  const categoriasConsulta = useVitrina(null)
  const mutaciones = useMutacionesProductos()

  const [formulario, setFormulario] = useState<Borrador | null>(null)
  const [imagen, setImagen] = useState<File | null>(null)
  const [vistaPrevia, setVistaPrevia] = useState<string | null>(null)
  const [errores, setErrores] = useState<Record<string, string>>({})
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')
  const [confirmacion, setConfirmacion] = useState<ProductoAdministrativo | null>(null)
  const formularioRef = useRef<HTMLFormElement>(null)

  const productos = consulta.data?.resultados ?? []
  const categorias = categoriasConsulta.data?.categorias ?? []
  const guardando = mutaciones.crear.isPending || mutaciones.actualizar.isPending
  const ocupado = guardando || mutaciones.eliminar.isPending

  const productoEditado = formulario?.id
    ? productos.find((producto) => producto.id === formulario.id)
    : undefined
  const imagenMostrada = vistaPrevia ?? productoEditado?.imagen.url ?? null

  useEffect(() => {
    return () => {
      if (vistaPrevia) URL.revokeObjectURL(vistaPrevia)
    }
  }, [vistaPrevia])

  function cambiarImagen(archivo: File | null) {
    if (vistaPrevia) URL.revokeObjectURL(vistaPrevia)
    setImagen(archivo)
    setVistaPrevia(archivo ? URL.createObjectURL(archivo) : null)
    if (archivo) {
      setErrores((actuales) => {
        const siguientes = { ...actuales }
        delete siguientes.imagen
        return siguientes
      })
    }
  }

  function abrirCrear() {
    setMensaje('')
    setError('')
    setErrores({})
    cambiarImagen(null)
    setFormulario({
      nombre: '',
      categoria: '',
      descripcion: '',
      imagenAlt: '',
      visible: true,
    })
  }

  function abrirEditar(producto: ProductoAdministrativo) {
    setMensaje('')
    setError('')
    setErrores({})
    cambiarImagen(null)
    setFormulario({
      id: producto.id,
      nombre: producto.nombre,
      categoria: producto.categoria.slug,
      descripcion: producto.descripcion,
      imagenAlt: producto.imagen.alt,
      visible: producto.visible,
    })
  }

  function cerrarFormulario() {
    if (guardando) return
    setFormulario(null)
    setErrores({})
    setError('')
    cambiarImagen(null)
  }

  function seleccionarImagen(evento: ChangeEvent<HTMLInputElement>) {
    const archivo = evento.target.files?.[0] ?? null
    const errorArchivo = validarImagen(archivo)
    if (errorArchivo) {
      evento.target.value = ''
      setErrores((actuales) => ({ ...actuales, imagen: errorArchivo }))
      return
    }
    cambiarImagen(archivo)
  }

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!formulario) return
    setMensaje('')
    setError('')

    const siguientes: Record<string, string> = {}
    if (!formulario.nombre.trim()) siguientes.nombre = 'Escribe el nombre del producto.'
    if (!formulario.categoria) siguientes.categoria = 'Selecciona una categoría.'
    if (!formulario.descripcion.trim()) siguientes.descripcion = 'Escribe una descripción.'
    if (!formulario.imagenAlt.trim()) {
      siguientes.imagen_alt = 'Describe la imagen con un texto alternativo.'
    }
    if (!formulario.id && !imagen) siguientes.imagen = 'Selecciona una imagen.'
    const errorArchivo = validarImagen(imagen)
    if (errorArchivo) siguientes.imagen = errorArchivo

    if (Object.keys(siguientes).length > 0) {
      setErrores(siguientes)
      // El DOM aún no refleja `aria-invalid`; se enfoca después del commit para
      // llevar al usuario al primer campo con error.
      requestAnimationFrame(() => {
        formularioRef.current?.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus()
      })
      return
    }

    setErrores({})
    const datos = {
      nombre: formulario.nombre.trim(),
      categoria: formulario.categoria,
      descripcion: formulario.descripcion.trim(),
      imagen_alt: formulario.imagenAlt.trim(),
      visible: formulario.visible,
      ...(imagen ? { imagen } : {}),
    }

    try {
      if (formulario.id) {
        await mutaciones.actualizar.mutateAsync({ id: formulario.id, datos })
        setMensaje('Producto actualizado.')
      } else {
        if (!imagen) return
        await mutaciones.crear.mutateAsync({ ...datos, imagen })
        setMensaje('Producto creado.')
      }
      setFormulario(null)
      cambiarImagen(null)
    } catch (razon) {
      setErrores(erroresDeCampo(razon))
      setError(mensajeDeError(razon, 'No se pudo guardar el producto.'))
    }
  }

  async function alternarVisible(producto: ProductoAdministrativo) {
    setMensaje('')
    setError('')
    try {
      await mutaciones.actualizar.mutateAsync({
        id: producto.id,
        datos: { visible: !producto.visible },
      })
      setMensaje(
        producto.visible
          ? 'Producto oculto. Puedes volver a mostrarlo cuando quieras.'
          : 'Producto visible en la vitrina pública.',
      )
    } catch (razon) {
      setError(mensajeDeError(razon, 'No se pudo cambiar la visibilidad del producto.'))
    }
  }

  async function eliminarProducto() {
    if (!confirmacion) return
    const producto = confirmacion
    setConfirmacion(null)
    setMensaje('')
    setError('')
    try {
      await mutaciones.eliminar.mutateAsync(producto.id)
      setMensaje('Producto oculto. Puedes volver a mostrarlo desde este panel.')
    } catch (razon) {
      setError(mensajeDeError(razon, 'No se pudo ocultar el producto.'))
    }
  }

  return (
    <section className="admin-page" aria-labelledby="productos-titulo">
      <AdminConfirmDialog
        open={confirmacion !== null}
        title="Ocultar producto"
        description={`“${confirmacion?.nombre ?? ''}” dejará de mostrarse en la vitrina pública. La información y la imagen se conservan en este panel, así que podrás volver a mostrarlo cuando quieras.`}
        confirmLabel="Ocultar producto"
        onCancel={() => setConfirmacion(null)}
        onConfirm={() => void eliminarProducto()}
      />

      <div className="admin-page__intro">
        <div>
          <p className="admin-kicker">Vitrina pública</p>
          <h1 id="productos-titulo">Productos</h1>
          <p className="admin-lead">
            Publica, edita u oculta los productos que se muestran en la página pública.
          </p>
        </div>
        <button className="admin-button" type="button" onClick={abrirCrear} disabled={ocupado}>
          <Plus size={17} aria-hidden="true" />
          Nuevo producto
        </button>
      </div>

      {mensaje && (
        <p className="admin-feedback admin-feedback--success" role="status">
          {mensaje}
        </p>
      )}
      {error && (
        <div className="admin-feedback admin-feedback--error" role="alert">
          <p>{error}</p>
        </div>
      )}

      {consulta.isLoading && (
        <p className="admin-feedback" role="status">
          Cargando productos…
        </p>
      )}
      {consulta.isError && (
        <div className="admin-feedback admin-feedback--error" role="alert">
          <p>{mensajeDeError(consulta.error, 'No se pudo cargar el listado de productos.')}</p>
          <button className="admin-button" type="button" onClick={() => void consulta.refetch()}>
            Reintentar
          </button>
        </div>
      )}

      {formulario && (
        <section className="admin-panel admin-vitrina-formulario" aria-labelledby="producto-form-titulo">
          <div className="admin-section-heading">
            <div>
              <p className="admin-kicker">{formulario.id ? 'Edición' : 'Publicación'}</p>
              <h2 id="producto-form-titulo">
                {formulario.id ? 'Editar producto' : 'Nuevo producto'}
              </h2>
            </div>
            <button
              className="admin-button admin-button--secondary"
              type="button"
              onClick={cerrarFormulario}
              disabled={guardando}
            >
              Cancelar
            </button>
          </div>

          <form
            key={formulario.id ?? 'nuevo'}
            ref={formularioRef}
            className="admin-inline-form admin-vitrina-form"
            onSubmit={guardar}
            noValidate
          >
            <div className="admin-form-grid">
              <div className="admin-field">
                <label htmlFor="producto-nombre">Nombre</label>
                <input
                  id="producto-nombre"
                  value={formulario.nombre}
                  onChange={(evento) =>
                    setFormulario((actual) => (actual ? { ...actual, nombre: evento.target.value } : actual))
                  }
                  aria-invalid={Boolean(errores.nombre)}
                  aria-describedby={errores.nombre ? 'producto-nombre-error' : undefined}
                  autoFocus
                  disabled={guardando}
                />
                <ErrorCampo id="producto-nombre-error" mensaje={errores.nombre} />
              </div>

              <div className="admin-field">
                <label htmlFor="producto-categoria">Categoría</label>
                <select
                  id="producto-categoria"
                  value={formulario.categoria}
                  onChange={(evento) =>
                    setFormulario((actual) => (actual ? { ...actual, categoria: evento.target.value } : actual))
                  }
                  aria-invalid={Boolean(errores.categoria)}
                  aria-describedby={errores.categoria ? 'producto-categoria-error' : undefined}
                  disabled={guardando || categoriasConsulta.isLoading}
                >
                  <option value="">Selecciona una categoría</option>
                  {categorias.map((categoria) => (
                    <option key={categoria.slug} value={categoria.slug}>
                      {categoria.nombre}
                    </option>
                  ))}
                </select>
                <ErrorCampo id="producto-categoria-error" mensaje={errores.categoria} />
                {categoriasConsulta.isLoading && (
                  <p className="admin-vitrina-ayuda" role="status">
                    Cargando categorías…
                  </p>
                )}
                {categoriasConsulta.isError && (
                  <p className="admin-vitrina-error-campo" role="alert">
                    No pudimos cargar las categorías.{' '}
                    <button
                      className="admin-vitrina-enlace"
                      type="button"
                      onClick={() => void categoriasConsulta.refetch()}
                    >
                      Reintentar
                    </button>
                  </p>
                )}
              </div>

              <div className="admin-field admin-vitrina-form__ancho">
                <label htmlFor="producto-descripcion">Descripción</label>
                <textarea
                  id="producto-descripcion"
                  rows={3}
                  value={formulario.descripcion}
                  onChange={(evento) =>
                    setFormulario((actual) =>
                      actual ? { ...actual, descripcion: evento.target.value } : actual,
                    )
                  }
                  aria-invalid={Boolean(errores.descripcion)}
                  aria-describedby={errores.descripcion ? 'producto-descripcion-error' : undefined}
                  disabled={guardando}
                />
                <ErrorCampo id="producto-descripcion-error" mensaje={errores.descripcion} />
              </div>

              <div className="admin-field">
                <label htmlFor="producto-imagen-alt">Texto alternativo de la imagen</label>
                <input
                  id="producto-imagen-alt"
                  value={formulario.imagenAlt}
                  onChange={(evento) =>
                    setFormulario((actual) =>
                      actual ? { ...actual, imagenAlt: evento.target.value } : actual,
                    )
                  }
                  aria-invalid={Boolean(errores.imagen_alt)}
                  aria-describedby={
                    errores.imagen_alt
                      ? 'producto-imagen-alt-ayuda producto-imagen-alt-error'
                      : 'producto-imagen-alt-ayuda'
                  }
                  disabled={guardando}
                />
                <p className="admin-vitrina-ayuda" id="producto-imagen-alt-ayuda">
                  Describe la imagen para quienes usan lectores de pantalla.
                </p>
                <ErrorCampo id="producto-imagen-alt-error" mensaje={errores.imagen_alt} />
              </div>

              <div className="admin-field">
                <label className="admin-check" htmlFor="producto-visible">
                  <input
                    id="producto-visible"
                    type="checkbox"
                    checked={formulario.visible}
                    onChange={(evento) =>
                      setFormulario((actual) =>
                        actual ? { ...actual, visible: evento.target.checked } : actual,
                      )
                    }
                    disabled={guardando}
                  />
                  Visible en la vitrina pública
                </label>
                <p className="admin-vitrina-ayuda">
                  Si está desmarcado, el producto se conserva en el panel pero no se muestra al
                  público.
                </p>
              </div>

              <div className="admin-field admin-vitrina-form__ancho">
                <label htmlFor="producto-imagen">
                  Imagen {formulario.id ? '(opcional para reemplazar)' : ''}
                </label>
                <input
                  id="producto-imagen"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={seleccionarImagen}
                  aria-invalid={Boolean(errores.imagen)}
                  aria-describedby={
                    errores.imagen
                      ? 'producto-imagen-ayuda producto-imagen-error'
                      : 'producto-imagen-ayuda'
                  }
                  disabled={guardando}
                />
                <p className="admin-vitrina-ayuda" id="producto-imagen-ayuda">
                  JPG, PNG o WEBP. Máximo 5 MB. El servidor valida el archivo.
                </p>
                <ErrorCampo id="producto-imagen-error" mensaje={errores.imagen} />
                {imagenMostrada ? (
                  <div className="admin-vitrina-vista-previa">
                    <img src={imagenMostrada} alt="Vista previa de la imagen del producto" />
                    <p>{imagen ? 'Vista previa de la nueva imagen.' : 'Imagen actual.'}</p>
                  </div>
                ) : (
                  <p className="admin-vitrina-vista-previa admin-vitrina-vista-previa--vacia">
                    <ImageOff size={18} aria-hidden="true" />
                    Aún no hay una imagen seleccionada.
                  </p>
                )}
              </div>
            </div>

            <div className="admin-form-actions">
              <button className="admin-button" type="submit" disabled={guardando}>
                {guardando ? 'Guardando…' : formulario.id ? 'Guardar cambios' : 'Crear producto'}
              </button>
              <button
                className="admin-button admin-button--secondary"
                type="button"
                onClick={cerrarFormulario}
                disabled={guardando}
              >
                Cancelar
              </button>
            </div>
          </form>
        </section>
      )}

      {consulta.isSuccess && productos.length === 0 && (
        <div className="admin-empty">
          <h2>Todavía no hay productos</h2>
          <p>Crea el primer producto para preparar la vitrina pública.</p>
          <button className="admin-button" type="button" onClick={abrirCrear}>
            Crear producto
          </button>
        </div>
      )}

      {productos.length > 0 && (
        <section className="admin-panel" aria-labelledby="lista-productos-titulo">
          <div className="admin-section-heading">
            <div>
              <h2 id="lista-productos-titulo">Catálogo administrativo</h2>
              <p className="admin-section-note">
                {productos.length} producto{productos.length === 1 ? '' : 's'}, incluidos los
                ocultos.
              </p>
            </div>
          </div>

          <ul className="admin-vitrina-lista">
            {productos.map((producto) => (
              <li key={producto.id}>
                <article className="admin-vitrina-item">
                  <div className="admin-vitrina-item__media">
                    <img src={producto.imagen.url} alt="" loading="lazy" />
                  </div>
                  <div className="admin-vitrina-item__cuerpo">
                    <div className="admin-vitrina-item__cabecera">
                      <div>
                        <h3>{producto.nombre}</h3>
                        <p className="admin-muted">{producto.categoria.nombre}</p>
                      </div>
                      <span
                        className={`admin-status admin-vitrina-estado--${producto.visible ? 'visible' : 'oculto'}`}
                      >
                        {producto.visible ? 'Visible' : 'Oculto'}
                      </span>
                    </div>

                    <p className="admin-vitrina-descripcion">{producto.descripcion}</p>
                    <p className="admin-vitrina-alt">
                      <strong>Texto alternativo:</strong> {producto.imagen.alt}
                    </p>

                    <dl className="admin-vitrina-fechas">
                      <div>
                        <dt>Creado</dt>
                        <dd>
                          <time dateTime={producto.fecha_creacion}>
                            {fechaLegible(producto.fecha_creacion)}
                          </time>
                        </dd>
                      </div>
                      <div>
                        <dt>Actualizado</dt>
                        <dd>
                          <time dateTime={producto.fecha_actualizacion}>
                            {fechaLegible(producto.fecha_actualizacion)}
                          </time>
                        </dd>
                      </div>
                    </dl>

                    <div className="admin-vitrina-acciones">
                      <button
                        className="admin-button admin-button--secondary"
                        type="button"
                        onClick={() => abrirEditar(producto)}
                        disabled={ocupado}
                        aria-label={`Editar ${producto.nombre}`}
                      >
                        <Pencil size={16} aria-hidden="true" />
                        Editar
                      </button>
                      <button
                        className="admin-button admin-button--secondary"
                        type="button"
                        onClick={() => void alternarVisible(producto)}
                        disabled={ocupado}
                        aria-label={`${producto.visible ? 'Ocultar' : 'Mostrar'} ${producto.nombre}`}
                      >
                        {producto.visible ? (
                          <EyeOff size={16} aria-hidden="true" />
                        ) : (
                          <Eye size={16} aria-hidden="true" />
                        )}
                        {producto.visible ? 'Ocultar' : 'Mostrar'}
                      </button>
                      <button
                        className="admin-button admin-button--danger"
                        type="button"
                        onClick={() => setConfirmacion(producto)}
                        disabled={ocupado}
                        aria-label={`Eliminar ${producto.nombre}`}
                      >
                        <Trash size={16} aria-hidden="true" />
                        Eliminar
                      </button>
                    </div>
                  </div>
                </article>
              </li>
            ))}
          </ul>
        </section>
      )}
    </section>
  )
}

export default AdminProductos
