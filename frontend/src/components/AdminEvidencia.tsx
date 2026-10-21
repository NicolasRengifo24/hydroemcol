import { useState, type FormEvent } from 'react'
import { useMutacionesAdministrativas } from '../hooks/useAdministrativo'
import type { DatosRegistroTecnico, Fotografia, RegistroTecnico, TipoFotografia } from '../services/api'
import { mensajeDeError } from '../services/errores'
import { AdminConfirmDialog } from './AdminConfirmDialog'

function errorLegible(error: unknown) {
  return mensajeDeError(error, 'La operación no pudo completarse. Intenta nuevamente.')
}

const tipos: TipoFotografia[] = ['RECEPCION', 'DIAGNOSTICO', 'REPARACION', 'PRUEBA', 'OTRO']

export function RegistroTecnicoPanel({ registro, servicioId }: { registro: RegistroTecnico | null; servicioId: number }) {
  const mutaciones = useMutacionesAdministrativas(servicioId)
  const [editando, setEditando] = useState(Boolean(registro))
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')

  const enviar = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(''); setExito('')
    const formulario = new FormData(event.currentTarget)
    const datos: DatosRegistroTecnico = {
      diagnostico: String(formulario.get('diagnostico') || ''),
      trabajo_realizado: String(formulario.get('trabajo_realizado') || ''),
      resultado_pruebas: String(formulario.get('resultado_pruebas') || ''),
      recomendaciones: String(formulario.get('recomendaciones') || ''),
      observaciones: String(formulario.get('observaciones_tecnicas') || ''),
    }
    try {
      if (registro) await mutaciones.actualizarRegistroTecnico.mutateAsync(datos)
      else await mutaciones.crearRegistroTecnico.mutateAsync(datos)
      setExito('Registro técnico guardado.'); setEditando(false)
    } catch (reason) { setError(errorLegible(reason)) }
  }

  return <section className="admin-panel admin-panel--internal" aria-labelledby="tecnico-titulo">
    <div className="admin-section-heading"><div><p className="admin-kicker">Solo uso interno</p><h2 id="tecnico-titulo">Registro técnico</h2></div>{registro && !editando && <button className="admin-button admin-button--secondary" type="button" onClick={() => setEditando(true)}>Editar registro</button>}</div>
    <p className="admin-section-note">Texto libre interno. No se muestra en el seguimiento del cliente.</p>
    {exito && <p className="admin-feedback admin-feedback--success" role="status">{exito}</p>}
    {error && <p className="admin-form-error" role="alert">{error}</p>}
    {editando ? <form className="admin-inline-form" onSubmit={enviar}>
      <label>Diagnóstico<textarea name="diagnostico" rows={3} defaultValue={registro?.diagnostico} /></label>
      <label>Trabajo realizado<textarea name="trabajo_realizado" rows={3} defaultValue={registro?.trabajo_realizado} /></label>
      <label>Resultado de pruebas<textarea name="resultado_pruebas" rows={3} defaultValue={registro?.resultado_pruebas} /></label>
      <label>Recomendaciones<textarea name="recomendaciones" rows={3} defaultValue={registro?.recomendaciones} /></label>
      <label>Observaciones técnicas<textarea name="observaciones_tecnicas" rows={3} defaultValue={registro?.observaciones} /></label>
      <div className="admin-form-actions"><button className="admin-button" type="submit" disabled={mutaciones.crearRegistroTecnico.isPending || mutaciones.actualizarRegistroTecnico.isPending}>Guardar registro</button>{registro && <button className="admin-button admin-button--secondary" type="button" onClick={() => setEditando(false)}>Cancelar</button>}</div>
    </form> : registro ? <dl className="admin-data-grid">{[['Diagnóstico', registro.diagnostico], ['Trabajo realizado', registro.trabajo_realizado], ['Resultado de pruebas', registro.resultado_pruebas], ['Recomendaciones', registro.recomendaciones], ['Observaciones', registro.observaciones]].map(([titulo, valor]) => <div key={titulo}><dt>{titulo}</dt><dd>{valor || '—'}</dd></div>)}<div><dt>Última actualización</dt><dd>{registro.actualizado_por || 'Sistema'} · {new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(registro.fecha_actualizacion))}</dd></div></dl> : <div className="admin-empty"><p>No hay registro técnico. Créalo cuando exista información para documentar.</p><button className="admin-button" type="button" onClick={() => setEditando(true)}>Crear registro técnico</button></div>}
  </section>
}

export function FotografiasPanel({ fotografias, servicioId }: { fotografias: Fotografia[]; servicioId: number }) {
  const mutaciones = useMutacionesAdministrativas(servicioId)
  const [error, setError] = useState(''); const [exito, setExito] = useState(''); const [previsualizacion, setPrevisualizacion] = useState('')
  const [editando, setEditando] = useState<number | null>(null)
  const [fotoParaEliminar, setFotoParaEliminar] = useState<number | null>(null)
  const formulario = (foto?: Fotografia) => <form className="admin-inline-form" onSubmit={async (event) => { event.preventDefault(); setError(''); setExito(''); const data = new FormData(event.currentTarget); const datos = { descripcion: String(data.get('descripcion') || ''), tipo: data.get('tipo') as TipoFotografia, visible_cliente: data.get('visible_cliente') === 'on' }; try { if (foto) await mutaciones.actualizarFotografia.mutateAsync({ id: foto.id, datos }); else { const archivo = data.get('archivo'); if (!(archivo instanceof File) || !archivo.size) throw new Error('Selecciona una fotografía.'); const carga = new FormData(); carga.append('archivo', archivo); carga.append('descripcion', datos.descripcion); carga.append('tipo', datos.tipo); carga.append('visible_cliente', String(datos.visible_cliente)); await mutaciones.crearFotografia.mutateAsync(carga) } setExito(foto ? 'Fotografía actualizada.' : 'Fotografía cargada.'); setEditando(null); setPrevisualizacion('') } catch (reason) { setError(errorLegible(reason)) }}}>
    {!foto && <label>Archivo (JPG, JPEG o PNG)<input name="archivo" type="file" accept="image/jpeg,image/png" required onChange={(event) => setPrevisualizacion(event.target.files?.[0] ? URL.createObjectURL(event.target.files[0]) : '')} /></label>}
    <label>Descripción<textarea name="descripcion" rows={2} defaultValue={foto?.descripcion} /></label><label>Tipo<select name="tipo" defaultValue={foto?.tipo || 'RECEPCION'}>{tipos.map((tipo) => <option key={tipo} value={tipo}>{tipo}</option>)}</select></label><label className="admin-check"><input name="visible_cliente" type="checkbox" defaultChecked={foto?.visible_cliente} /> Visible para el cliente</label>{previsualizacion && <img className="admin-photo-preview" src={previsualizacion} alt="Vista previa de la fotografía seleccionada" />}<div className="admin-form-actions"><button className="admin-button" type="submit" disabled={mutaciones.crearFotografia.isPending || mutaciones.actualizarFotografia.isPending}>{foto ? 'Guardar cambios' : 'Cargar fotografía'}</button><button className="admin-button admin-button--secondary" type="button" onClick={() => { setEditando(null); setPrevisualizacion('') }}>Cancelar</button></div>
  </form>
  const eliminarFotografia = async () => { if (fotoParaEliminar === null) return; try { await mutaciones.eliminarFotografia.mutateAsync(fotoParaEliminar); setExito('Fotografía eliminada.'); setError('') } catch (reason) { setError(errorLegible(reason)) } finally { setFotoParaEliminar(null) } }
  return <section className="admin-panel" aria-labelledby="fotografias-titulo"><AdminConfirmDialog open={fotoParaEliminar !== null} title="Eliminar fotografía" description="Esta fotografía se eliminará de forma permanente y no podrá recuperarse." confirmLabel="Eliminar fotografía" danger onCancel={() => setFotoParaEliminar(null)} onConfirm={() => void eliminarFotografia()} /><div className="admin-section-heading"><div><h2 id="fotografias-titulo">Fotografías</h2><p className="admin-section-note">{fotografias.length} de 10 almacenadas</p></div>{fotografias.length < 10 && editando !== 0 && <button className="admin-button" type="button" onClick={() => setEditando(0)}>Agregar fotografía</button>}</div>{exito && <p className="admin-feedback admin-feedback--success" role="status">{exito}</p>}{error && <p className="admin-form-error" role="alert">{error}</p>}{editando === 0 && formulario()}{fotografias.length === 0 && editando !== 0 && <p className="admin-muted">No hay fotografías almacenadas.</p>}<div className="admin-photo-grid">{fotografias.map((foto) => <article className="admin-photo-card" key={foto.id}><img src={foto.url} alt={foto.descripcion || `Fotografía ${foto.tipo}`} /><div><strong>{foto.tipo}</strong><p>{foto.descripcion || 'Sin descripción.'}</p><p className="admin-muted">{foto.visible_cliente ? 'Visible para el cliente' : 'Solo interna'}</p><div className="admin-action-row"><button className="admin-button admin-button--secondary" type="button" onClick={() => setEditando(foto.id)}>Editar</button><button className="admin-button admin-button--danger" type="button" onClick={() => setFotoParaEliminar(foto.id)}>Eliminar</button></div>{editando === foto.id && formulario(foto)}</div></article>)}</div></section>
}
