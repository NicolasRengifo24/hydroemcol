import { HeroNosotros } from "../components/nosotros/HeroNosotros";
import { BloqueQuienesSomos } from "../components/nosotros/BloqueQuienesSomos";
import { BloqueIdentidad } from "../components/nosotros/BloqueIdentidad";
import { BloqueUbicacion } from "../components/nosotros/BloqueUbicacion";
import { CTANosotros } from "../components/nosotros/CTANosotros";

// El `<main>` lo renderiza Layout; aquí solo va la lista de secciones, como en
// Inicio. `nosotros.css` ya lo importa cada componente; no se duplica aquí.
// Un único `h1`: el del hero (RF-1.3, RNF-3).
// La sección de capacidades técnicas se omite por decisión del usuario; los
// textos siguen disponibles en components/inicio/contenido.ts y el componente
// BloqueCapacidades se conserva para reutilizarlo si se vuelve a necesitar.
function Nosotros() {
  return (
    <>
      <HeroNosotros />
      <BloqueQuienesSomos />
      <BloqueIdentidad />
      <BloqueUbicacion />
      <CTANosotros />
    </>
  );
}

export default Nosotros;
