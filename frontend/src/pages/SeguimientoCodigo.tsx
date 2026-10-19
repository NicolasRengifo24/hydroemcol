import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

function SeguimientoCodigo() {
  const [token, setToken] = useState('')
  const navigate = useNavigate()

  const buscar = (evento: FormEvent<HTMLFormElement>) => {
    evento.preventDefault()
    const tokenLimpio = token.trim()
    if (tokenLimpio) navigate(`/seguimiento/${encodeURIComponent(tokenLimpio)}`)
  }

  return (
    <section className="page seguimiento">
      <h1>Seguimiento de servicio</h1>
      <p>Consulta la información disponible usando el enlace privado que recibiste.</p>
      <form className="seguimiento__busqueda" onSubmit={buscar}>
        <label htmlFor="token-seguimiento">Token de seguimiento</label>
        <input id="token-seguimiento" value={token} onChange={(evento) => setToken(evento.target.value)} required autoComplete="off" />
        <button className="seguimiento__boton" type="submit">Consultar servicio</button>
      </form>
    </section>
  )
}

export default SeguimientoCodigo
