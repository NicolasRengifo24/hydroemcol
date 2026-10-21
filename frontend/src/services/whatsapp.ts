export function construirUrlWhatsApp(numeroDestino: string, texto: string): string {
  return `https://wa.me/${numeroDestino}?text=${encodeURIComponent(texto)}`
}

export function abrirWhatsApp(url: string): boolean {
  const ventana = window.open(url, '_blank')
  if (!ventana) return false
  ventana.opener = null
  return true
}
