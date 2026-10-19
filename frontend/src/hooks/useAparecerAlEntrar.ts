import { useEffect, useRef, useState } from 'react'

// Indica cuándo un elemento entra en la ventana por primera vez (IntersectionObserver).
// Solo sirve para la entrada suave por CSS: la clase `revelar` oculta el bloque únicamente
// bajo `prefers-reduced-motion: no-preference`; con movimiento reducido todo es visible.
// Una vez visible, el observador se desconecta: no hay animación al volver a hacer scroll.
export function useAparecerAlEntrar<T extends HTMLElement>() {
  const ref = useRef<T>(null)
  const [visible, setVisible] = useState(() => typeof IntersectionObserver === 'undefined')

  useEffect(() => {
    const elemento = ref.current
    if (visible || !elemento) return

    const observador = new IntersectionObserver(
      (entradas) => {
        if (entradas.some((entrada) => entrada.isIntersecting)) {
          setVisible(true)
          observador.disconnect()
        }
      },
      { threshold: 0.12, rootMargin: '0px 0px -6% 0px' },
    )
    observador.observe(elemento)

    return () => observador.disconnect()
  }, [visible])

  return { ref, visible }
}
