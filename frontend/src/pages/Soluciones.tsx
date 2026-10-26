import { Link } from "react-router-dom";
import { ArrowRight, BadgeCheck, Gauge, MapPin, Ship, Wrench } from "lucide-react";
import "./Soluciones.css";

const productos = [
  {
    src: "/img/soluciones/productos-1.jpeg",
    alt: "Kit de reparación de bomba hidráulica con pistones, placas y sellos.",
    titulo: "Kits de reparación",
    texto:
      "Kits con bloque de cilindros, pistones, placas de válvulas, platos de empuje y sellos para recuperar el rendimiento de bombas hidráulicas.",
  },
  {
    src: "/img/soluciones/productos-2.jpeg",
    alt: "Bloques de cilindros, placas de válvulas y pistones de una bomba hidráulica.",
    titulo: "Componentes hidráulicos",
    texto:
      "Bloques de cilindros, placas de válvulas, pistones y conjuntos para mantenimiento de sistemas hidráulicos.",
  },
  {
    src: "/img/soluciones/productos-3.jpeg",
    alt: "Conjunto de piezas para reparación hidráulica y búsqueda de referencias especiales.",
    titulo: "Repuestos sobre pedido",
    texto:
      "Búsqueda e importación de referencias especiales y repuestos no comunes para tu operación.",
  },
];

const servicios = [
  {
    src: "/img/soluciones/banco-pruebas.jpeg",
    alt: "Bomba hidráulica CAT 236 instalada en el banco de pruebas.",
    titulo: "Reparación de bomba CAT 236",
    texto:
      "Reparación integral y prueba en banco con verificación de flujo y presión para validar el desempeño de la bomba bajo condiciones controladas.",
  },
  {
    src: "/img/soluciones/banco-pruebas-2.jpeg",
    alt: "Bomba hidráulica Itachi 70 durante su prueba en banco.",
    titulo: "Reparación de bomba Itachi 70",
    texto:
      "Reparación y prueba en banco de la bomba Itachi 70, incluyendo corrección de regulación y calado del motor para recuperar su operación.",
  },
  {
    src: "/img/soluciones/grua-telescopica-mantenimiento.jpeg",
    alt: "Componentes de grúa telescópica durante su desarme técnico.",
    titulo: "Desarme de grúa telescópica",
    texto:
      "Desarme técnico de grúa telescópica para traslado helicoportado en el Putumayo, con preparación de componentes para transporte en condiciones exigentes.",
  },
  {
    src: "/img/soluciones/mantenimiento-finisher.jpeg",
    alt: "Soporte técnico a una finisher de asfalto en campo.",
    titulo: "Soporte técnico a finisher de asfalto",
    texto:
      "Mantenimiento y soporte en campo a finisher de asfalto en Palmira, Valle, enfocado en restablecer la confiabilidad del equipo y la continuidad de la operación.",
  },
  {
    src: "/img/soluciones/mantenimiento-hidroituango.jpeg",
    alt: "Equipos y obra de infraestructura en Hidroituango.",
    titulo: "Mantenimiento de equipos en Hidroituango",
    texto:
      "Soporte técnico y mantenimiento de equipos múltiples en Hidroituango, atendiendo requerimientos hidráulicos en un entorno de infraestructura de alta exigencia.",
  },
  {
    src: "/img/soluciones/relleno-juana.jpeg",
    alt: "Excavadora durante mantenimiento en el Relleno Sanitario Doña Juana.",
    titulo: "Mantenimiento de excavadora en Doña Juana",
    texto:
      "Mantenimiento y soporte técnico de excavadora en el Relleno Sanitario Doña Juana, con atención a sistemas hidráulicos bajo condiciones operativas exigentes.",
  },
];

function SolucionCard({
  src,
  alt,
  titulo,
  texto,
}: {
  src: string;
  alt: string;
  titulo: string;
  texto: string;
}) {
  return (
    <article className="solucion-card">
      <img
        className="solucion-card__imagen"
        src={src}
        alt={alt}
        loading="lazy"
        decoding="async"
      />
      <div className="solucion-card__contenido">
        <h3 className="solucion-card__titulo">{titulo}</h3>
        <p className="solucion-card__texto">{texto}</p>
      </div>
    </article>
  );
}

function ProductoCard({
  src,
  alt,
  titulo,
  texto,
  numero,
  destacado = false,
}: {
  src: string;
  alt: string;
  titulo: string;
  texto: string;
  numero: string;
  destacado?: boolean;
}) {
  return (
    <article
      className={`producto-card${destacado ? " producto-card--destacado" : ""}`}
    >
      <img
        className="producto-card__imagen"
        src={src}
        alt={alt}
        loading="lazy"
        decoding="async"
      />
      <div className="producto-card__contenido">
        <span className="producto-card__numero" aria-hidden="true">
          {numero}
        </span>
        <h3 className="producto-card__titulo">{titulo}</h3>
        <p className="producto-card__texto">{texto}</p>
      </div>
    </article>
  );
}

function Soluciones() {
  return (
    <div className="soluciones-page">
      <section
        className="soluciones-hero soluciones-hero--productos"
        aria-labelledby="hero-productos-titulo"
      >
        <div className="soluciones-hero__contenido">
          <p className="soluciones-hero__eyebrow">Repuestos e importación</p>
          <h1 id="hero-productos-titulo" className="soluciones-hero__titulo">
            Componentes para mantener tu operación en movimiento
          </h1>
          <p className="soluciones-hero__texto">
            Suministramos repuestos hidráulicos y gestionamos referencias
            especiales sobre pedido, con enfoque en calidad y precisión técnica.
          </p>
        </div>
      </section>

      <section className="soluciones-productos" aria-labelledby="productos-titulo">
        <div className="soluciones-productos__bento">
          <div className="soluciones-productos__intro">
            <p className="soluciones-section__eyebrow soluciones-productos__eyebrow">
              Venta de repuestos · Línea principal
            </p>
            <h2
              id="productos-titulo"
              className="soluciones-section__titulo soluciones-productos__titulo"
            >
              Repuestos y componentes hidráulicos
            </h2>
            <p className="soluciones-productos__texto">
              Kits, piezas y referencias especiales para diagnóstico,
              mantenimiento y reparación de equipos hidráulicos. Suministro de
              repuestos OEM y acompañamiento técnico para mantener la operación
              activa.
            </p>
            <ul className="soluciones-productos__beneficios">
              <li>
                <BadgeCheck size={18} strokeWidth={2} aria-hidden="true" />
                <span>
                  <strong>Repuestos OEM</strong> para las principales marcas.
                </span>
              </li>
              <li>
                <Ship size={18} strokeWidth={2} aria-hidden="true" />
                <span>
                  <strong>Importación sobre pedido</strong> de referencias
                  especiales.
                </span>
              </li>
              <li>
                <MapPin size={18} strokeWidth={2} aria-hidden="true" />
                <span>
                  <strong>Cobertura nacional</strong> para tu operación.
                </span>
              </li>
            </ul>
            <Link className="soluciones-productos__cta" to="/solicitar">
              Solicitar repuesto
              <ArrowRight size={18} strokeWidth={2.2} aria-hidden="true" />
            </Link>
          </div>
          {productos.map((producto, index) => (
            <ProductoCard
              key={producto.src}
              {...producto}
              numero={`0${index + 1}`}
              destacado={index === 0}
            />
          ))}
        </div>
      </section>

      <section
        className="soluciones-hero soluciones-hero--servicios"
        aria-labelledby="hero-servicios-titulo"
      >
        <div className="soluciones-hero__contenido">
          <p className="soluciones-hero__eyebrow">Servicio especializado</p>
          <h2 id="hero-servicios-titulo" className="soluciones-hero__titulo">
            Hidráulica que mueve grandes proyectos
          </h2>
          <p className="soluciones-hero__texto">
            Diagnóstico, pruebas, mantenimiento y soporte técnico para
            maquinaria y sistemas electrohidráulicos.
          </p>
        </div>
      </section>

      <section className="soluciones-servicios" aria-labelledby="servicios-titulo">
        <div className="soluciones-servicios__encabezado">
          <div className="soluciones-section__encabezado">
            <p className="soluciones-section__eyebrow">Servicios · Casos reales</p>
            <h2 id="servicios-titulo" className="soluciones-section__titulo">
              Capacidad técnica en campo y taller
            </h2>
            <p className="soluciones-section__intro">
              Experiencia aplicada en reparación, prueba en banco y soporte
              técnico de equipos hidráulicos en operaciones exigentes.
            </p>
          </div>
          <ul
            className="soluciones-servicios__capacidades"
            aria-label="Capacidades de servicio"
          >
            <li>
              <Gauge size={17} strokeWidth={2} aria-hidden="true" />
              <span>Banco de pruebas</span>
            </li>
            <li>
              <Wrench size={17} strokeWidth={2} aria-hidden="true" />
              <span>Reparación especializada</span>
            </li>
            <li>
              <MapPin size={17} strokeWidth={2} aria-hidden="true" />
              <span>Soporte en campo</span>
            </li>
          </ul>
        </div>
        <div className="soluciones-galeria soluciones-galeria--servicios">
          {servicios.map((servicio) => (
            <SolucionCard key={servicio.src} {...servicio} />
          ))}
        </div>
      </section>
    </div>
  );
}

export default Soluciones;
