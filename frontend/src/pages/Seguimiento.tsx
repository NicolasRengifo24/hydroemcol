import { useParams } from 'react-router-dom'

function Seguimiento() {
  const { token } = useParams<{ token: string }>()

  return (
    <section className="page">
      <h1>Seguimiento de servicio</h1>
      <p>Seguimiento del token <code>{token}</code> — contenido por definir (Fase 3).</p>
    </section>
  )
}

export default Seguimiento