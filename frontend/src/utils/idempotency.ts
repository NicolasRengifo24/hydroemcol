export function generateIdempotencyKey(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  // Fallback simple para entornos antiguos
  const array = new Uint8Array(16)
  if (typeof crypto !== 'undefined' && 'getRandomValues' in crypto) {
    (crypto as Crypto).getRandomValues(array)
  }
  // Formato UUID v4 aproximado
  array[6] = (array[6] & 0x0f) | 0x40
  array[8] = (array[8] & 0x3f) | 0x80
  const hex = Array.from(array)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
  return `${hex.substring(0, 8)}-${hex.substring(8, 12)}-${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20, 32)}`
}