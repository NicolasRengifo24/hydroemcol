import { Hero } from '../components/inicio/Hero'
import { BloqueServiciosDestacados } from '../components/inicio/BloqueServiciosDestacados'
import { BloqueCapacidadTecnica } from '../components/inicio/BloqueCapacidadTecnica'
import { BloquePasos } from '../components/inicio/BloquePasos'
import { CTASection } from '../components/inicio/CTASection'
import '../components/inicio/inicio.css'

function Inicio() {
  return (
    <>
      <Hero ctaTexto="Solicitar un servicio" ctaTo="/solicitar" />
      <BloqueServiciosDestacados />
      <BloqueCapacidadTecnica />
      <BloquePasos />
      <CTASection />
    </>
  )
}

export default Inicio
