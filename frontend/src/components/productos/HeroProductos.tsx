import { useCallback, useEffect, useState } from "react";
import type { KeyboardEvent } from "react";
import Logo from "../brand/Logo";
import { CONFIG_HERO_PRODUCTOS } from "../../config/heroProductos";
import { PIEZAS_HERO } from "../../config/piezasHero";
import { urlWhatsApp } from "../../config/sitio";
import "./HeroProductos.css";

const DURACION_AUTOPLAY_MS = 5600;
const DURACION_TRANSICION_MS = 760;

export function HeroProductos() {
  const piezas = PIEZAS_HERO.filter((pieza) => pieza.imagen);
  const [posicion, setPosicion] = useState(1);
  const [transicionActiva, setTransicionActiva] = useState(true);
  const [interaccionUsuario, setInteraccionUsuario] = useState(false);
  const [pausaPorPuntero, setPausaPorPuntero] = useState(false);
  const [pausaPorFoco, setPausaPorFoco] = useState(false);
  const [documentoOculto, setDocumentoOculto] = useState(
    () =>
      typeof document !== "undefined" && document.visibilityState === "hidden",
  );
  const [reducirMovimiento, setReducirMovimiento] = useState(false);
  const [swipeInicio, setSwipeInicio] = useState<number | null>(null);
  const indice =
    piezas.length === 0 ? 0 : (posicion - 1 + piezas.length) % piezas.length;
  const piezasVirtuales =
    piezas.length > 0 ? [piezas[piezas.length - 1], ...piezas, piezas[0]] : [];

  useEffect(() => {
    const consulta = window.matchMedia("(prefers-reduced-motion: reduce)");
    const actualizar = () => setReducirMovimiento(consulta.matches);
    actualizar();
    consulta.addEventListener("change", actualizar);
    return () => consulta.removeEventListener("change", actualizar);
  }, []);

  useEffect(() => {
    const actualizar = () =>
      setDocumentoOculto(document.visibilityState === "hidden");
    document.addEventListener("visibilitychange", actualizar);
    return () => document.removeEventListener("visibilitychange", actualizar);
  }, []);

  const mover = useCallback(
    (paso: number, manualCambio = true) => {
      if (piezas.length === 0) return;
      if (manualCambio) {
        setInteraccionUsuario(true);
      }
      setTransicionActiva(true);
      setPosicion((actual) => actual + paso);
    },
    [piezas.length],
  );

  useEffect(() => {
    if (
      piezas.length < 2 ||
      interaccionUsuario ||
      pausaPorPuntero ||
      pausaPorFoco ||
      documentoOculto ||
      reducirMovimiento
    )
      return;

    const temporizador = window.setInterval(
      () => mover(1, false),
      DURACION_AUTOPLAY_MS,
    );
    return () => window.clearInterval(temporizador);
  }, [
    piezas.length,
    documentoOculto,
    interaccionUsuario,
    mover,
    pausaPorPuntero,
    pausaPorFoco,
    reducirMovimiento,
  ]);

  const onKeyDown = (evento: KeyboardEvent<HTMLDivElement>) => {
    if (evento.key === "ArrowDown") {
      evento.preventDefault();
      mover(1);
    }
    if (evento.key === "ArrowUp") {
      evento.preventDefault();
      mover(-1);
    }
  };

  if (piezas.length === 0) return null;

  const deslizarPieza = (
    pieza: (typeof PIEZAS_HERO)[number],
    posicion: number,
  ) => {
    return (
      <article
        className={`hero-productos__diapositiva${posicion === indice ? " hero-productos__diapositiva--activa" : ""}`}
        role="group"
        aria-roledescription="diapositiva"
        aria-label={`${posicion + 1} de ${piezas.length}`}
        aria-hidden={posicion === indice ? undefined : true}
      >
        <div className="hero-productos__imagen-zona">
          <img
            src={pieza.imagen}
            alt={pieza.nombre || "Repuesto hidráulico de Hydroemcol"}
            loading={posicion === 0 ? "eager" : "lazy"}
            decoding="async"
            width={720}
            height={450}
          />
        </div>

        <div className="hero-productos__info">
          {pieza.tipo ? (
            <p className="hero-productos__tipo">{pieza.tipo}</p>
          ) : null}
          {pieza.nombre ? (
            <h2 className="hero-productos__nombre">{pieza.nombre}</h2>
          ) : null}
          {pieza.referencia ? (
            <p className="hero-productos__referencia">
              <span>Referencia</span>
              <strong>{pieza.referencia}</strong>
            </p>
          ) : null}
          {pieza.descripcion ? (
            <p className="hero-productos__descripcion">{pieza.descripcion}</p>
          ) : null}

          {pieza.estado || pieza.aplicacion ? (
            <dl className="hero-productos__datos">
              {pieza.estado ? (
                <div>
                  <dt>Estado</dt>
                  <dd>{pieza.estado}</dd>
                </div>
              ) : null}
              {pieza.aplicacion ? (
                <div>
                  <dt>Aplicación</dt>
                  <dd>{pieza.aplicacion}</dd>
                </div>
              ) : null}
            </dl>
          ) : null}

          <p className="hero-productos__disponibilidad">
            {pieza.stock ? "Disponible hoy" : "Consulta disponibilidad"}
          </p>

          {pieza.oem ? (
            <p
              className="hero-productos__oem"
              title="Equipo fabricado por el fabricante original"
            >
              Fabricante original
            </p>
          ) : null}
        </div>
      </article>
    );
  };

  const alTerminarTransicion = () => {
    if (posicion === piezas.length + 1) {
      setTransicionActiva(false);
      setPosicion(1);
      window.requestAnimationFrame(() => setTransicionActiva(true));
      return;
    }
    if (posicion === 0) {
      setTransicionActiva(false);
      setPosicion(piezas.length);
      window.requestAnimationFrame(() => setTransicionActiva(true));
    }
  };

  return (
    <section className="hero-productos" aria-labelledby="hero-productos-titulo">
      <div
        className="hero-productos__fondo"
        style={{ backgroundImage: `url("${CONFIG_HERO_PRODUCTOS.fondo}")` }}
        aria-hidden="true"
      />
      <div className="hero-productos__velo" aria-hidden="true" />

      <div className="hero-productos__contenido">
        <div className="hero-productos__copy">
          <p className="hero-productos__eyebrow">
            {CONFIG_HERO_PRODUCTOS.etiqueta}
          </p>
          <h1 id="hero-productos-titulo" className="hero-productos__titulo">
            {CONFIG_HERO_PRODUCTOS.tituloActivo}
          </h1>
          {CONFIG_HERO_PRODUCTOS.descripcion ? (
            <p className="hero-productos__texto">
              {CONFIG_HERO_PRODUCTOS.descripcion}
            </p>
          ) : null}

          <div className="hero-productos__acciones">
            <a
              className="hero-productos__principal"
              href={urlWhatsApp(
                "Hola, quiero preguntar por un repuesto hidráulico y solicitar una cotización.",
              )}
              target="_blank"
              rel="noopener noreferrer"
            >
              {CONFIG_HERO_PRODUCTOS.textoBotonPrincipal}
            </a>
          </div>
        </div>

        <div
          className="hero-productos__ventana"
          role="region"
          aria-roledescription="carrusel"
          aria-label="Piezas hidráulicas"
          tabIndex={0}
          onKeyDown={onKeyDown}
          onMouseEnter={() => setPausaPorPuntero(true)}
          onMouseLeave={() => setPausaPorPuntero(false)}
          onFocus={() => setPausaPorFoco(true)}
          onBlur={(evento) => {
            if (
              !evento.currentTarget.contains(
                evento.relatedTarget as Node | null,
              )
            ) {
              setPausaPorFoco(false);
            }
          }}
          onTouchStart={(evento) => setSwipeInicio(evento.touches[0].clientY)}
          onTouchEnd={(evento) => {
            if (swipeInicio === null) return;
            const diferencia = swipeInicio - evento.changedTouches[0].clientY;
            if (Math.abs(diferencia) > 45) mover(diferencia > 0 ? 1 : -1);
            setSwipeInicio(null);
          }}
        >
          <div className="hero-productos__barra">
            <div className="hero-productos__puntos" aria-hidden="true">
              <span />
              <span />
              <span />
            </div>
            <Logo grande={false} sobreOscuro />
          </div>

          <div className="hero-productos__viewport">
            <div
              className={`hero-productos__track${transicionActiva ? "" : " hero-productos__track--sin-transicion"}`}
              style={{
                transform: `translateY(-${posicion * 100}%)`,
                transitionDuration: reducirMovimiento
                  ? "120ms"
                  : `${DURACION_TRANSICION_MS}ms`,
              }}
              onTransitionEnd={alTerminarTransicion}
            >
              {piezasVirtuales.map((pieza, posicionVirtual) => (
                <div
                  className="hero-productos__slide"
                  key={`${posicionVirtual}-${pieza.imagen}`}
                >
                  {deslizarPieza(
                    pieza,
                    posicionVirtual === 0
                      ? piezas.length - 1
                      : posicionVirtual === piezas.length + 1
                        ? 0
                        : posicionVirtual - 1,
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
