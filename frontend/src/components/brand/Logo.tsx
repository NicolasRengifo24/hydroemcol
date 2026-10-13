import './marca.css'

interface LogoProps {
  mostrarTexto?: boolean
  grande?: boolean
  sobreOscuro?: boolean
  className?: string
}

function Logo({ mostrarTexto = true, grande = false, sobreOscuro = false, className }: LogoProps) {
  const clases = ['marca']
  if (grande) clases.push('marca--grande')
  if (sobreOscuro) clases.push('marca--sobre-oscuro')
  if (className) clases.push(className)

  if (mostrarTexto) {
    return (
      <span className={clases.join(' ')}>
        <img
          src="/logo-completo.jpg"
          alt="Hydroemcol Service and Parts S.A.S"
          width={1059}
          height={232}
          decoding="async"
          loading="eager"
          className="marca__imagen"
        />
      </span>
    )
  }

  return (
    <span className={clases.join(' ')}>
      <img
        src="/favicon.svg"
        alt="Hydroemcol"
        width={170}
        height={138}
        decoding="async"
        loading="eager"
        className="marca__imagen marca__imagen--icono"
      />
    </span>
  )
}

export default Logo