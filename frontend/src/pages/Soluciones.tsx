import "./Soluciones.css";

const productos = [
  {
    src: "/img/soluciones/productos-1.jpeg",
    alt: "Kit de reparación de componentes de una bomba hidráulica.",
    titulo: "Kits de reparación",
    texto:
      "Componentes organizados para recuperar el rendimiento de equipos hidráulicos.",
  },
  {
    src: "/img/soluciones/productos-2.jpeg",
    alt: "Componentes metálicos y conjuntos de una bomba hidráulica.",
    titulo: "Componentes hidráulicos",
    texto: "Repuestos y conjuntos para mantenimiento de sistemas hidráulicos.",
  },
  {
    src: "/img/soluciones/productos-3.jpeg",
    alt: "Conjunto desmontado de piezas para reparación hidráulica.",
    titulo: "Repuestos sobre pedido",
    texto:
      "Búsqueda e importación de referencias especiales para tu operación.",
  },
];

const servicios = [
  {
    src: "/img/soluciones/banco-pruebas.jpeg",
    alt: "Componente hidráulico instalado en un banco de pruebas.",
    titulo: "Banco de pruebas",
    texto:
      "Evaluación técnica de componentes hidráulicos y electrohidráulicos.",
  },
  {
    src: "/img/soluciones/banco-pruebas-2.jpeg",
    alt: "Banco de pruebas hidráulico con equipo conectado.",
    titulo: "Diagnóstico técnico",
    texto: "Revisión visual y funcional para orientar la reparación adecuada.",
  },
  {
    src: "/img/soluciones/grua-telescopica-mantenimiento.jpeg",
    alt: "Mantenimiento de una grúa telescópica.",
    titulo: "Mantenimiento de maquinaria",
    texto:
      "Atención técnica para equipos de trabajo pesado y sus sistemas hidráulicos.",
  },
  {
    src: "/img/soluciones/mantenimiento-finisher.jpeg",
    alt: "Personal realizando mantenimiento a una máquina pavimentadora.",
    titulo: "Soporte en campo",
    texto:
      "Acompañamiento técnico en equipos que mantienen activa la operación.",
  },
  {
    src: "/img/soluciones/mantenimiento-hidroituango.jpeg",
    alt: "Vista de una obra de infraestructura en Hidroituango.",
    titulo: "Proyectos industriales",
    texto:
      "Experiencia visual en entornos de infraestructura y operación exigente.",
  },
  {
    src: "/img/soluciones/relleno-juana.jpeg",
    alt: "Maquinaria pesada trabajando en un proyecto de movimiento de tierra.",
    titulo: "Equipos de trabajo pesado",
    texto: "Soluciones para maquinaria que trabaja en condiciones exigentes.",
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

      <section
        className="soluciones-section"
        aria-labelledby="productos-titulo"
      >
        <div className="soluciones-section__encabezado">
          <p className="soluciones-section__eyebrow">Productos</p>
          <h2 id="productos-titulo" className="soluciones-section__titulo">
            Repuestos y componentes hidráulicos
          </h2>
          <p className="soluciones-section__intro">
            Kits, piezas y referencias especiales para diagnóstico,
            mantenimiento y reparación de equipos hidráulicos.
          </p>
        </div>
        <div className="soluciones-galeria soluciones-galeria--productos">
          {productos.map((producto) => (
            <SolucionCard key={producto.src} {...producto} />
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

      <section
        className="soluciones-section"
        aria-labelledby="servicios-titulo"
      >
        <div className="soluciones-section__encabezado">
          <p className="soluciones-section__eyebrow">Servicios</p>
          <h2 id="servicios-titulo" className="soluciones-section__titulo">
            Capacidad técnica en campo y taller
          </h2>
          <p className="soluciones-section__intro">
            Una mirada a los equipos, entornos y tipos de trabajo donde
            aplicamos nuestras soluciones hidráulicas.
          </p>
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
