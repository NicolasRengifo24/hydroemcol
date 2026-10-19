import { HeroNosotros } from "../components/nosotros/HeroNosotros";
import { BloqueQuienesSomos } from "../components/nosotros/BloqueQuienesSomos";
import { BloqueIdentidad } from "../components/nosotros/BloqueIdentidad";
import { BloqueCapacidades } from "../components/nosotros/BloqueCapacidades";
import { BloqueUbicacion } from "../components/nosotros/BloqueUbicacion";
import { CTANosotros } from "../components/nosotros/CTANosotros";

// Orden exacto de las 6 secciones de RF-1.1 (spec 009): (1) hero, (2) quiénes
// somos, (3) identidad con la cita, (4) capacidades técnicas, (5) ubicación y
// mapa, (6) llamado a la acción final. No añadir secciones extra, ni sección
// de proceso/pasos, ni sección de marcas (RF-1.2, D-7; RF-6 eliminada).
// El `<main>` lo renderiza Layout; aquí solo va la lista de secciones, como en
// Inicio.
// `nosotros.css` ya lo importa cada componente; no se duplica aquí.
// Un único `h1`: el del hero (RF-1.3, RNF-3).
function Nosotros() {
  return (
    <>
      <HeroNosotros />
      <BloqueQuienesSomos />
      <BloqueIdentidad />
      <BloqueCapacidades />

      <BloqueUbicacion />
      <CTANosotros />
    </>
  );
}

export default Nosotros;
