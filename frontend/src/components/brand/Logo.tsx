import Tuerca from './Tuerca'
import './marca.css'

interface LogoProps {
  mostrarTexto?: boolean
  grande?: boolean
  className?: string
}

function Logo({ mostrarTexto = true, grande = false, className }: LogoProps) {
  const clases = ['marca']
  if (grande) clases.push('marca--grande')
  if (className) clases.push(className)

  return (
    <span className={clases.join(' ')}>
      <Tuerca className="marca__tuerca" />
      {mostrarTexto && (
        <span className="marca__texto">
          <span className="marca__nombre">HYDROEMCOL</span>
          <span className="marca__tagline">SERVICE AND PARTS S.A.S</span>
        </span>
      )}
    </span>
  )
}

export default Logo
