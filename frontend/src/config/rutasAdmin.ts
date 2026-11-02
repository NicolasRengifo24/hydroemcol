// Ruta base del panel administrativo. Se centraliza aquí para poder cambiarla
// en un solo punto. La protección real del panel es la autenticación del
// backend y Cloudflare Access, no el nombre de la ruta.
export const RUTA_ADMIN = '/control-operativo'
export const RUTA_ADMIN_LOGIN = `${RUTA_ADMIN}/login`
export const RUTA_ADMIN_RELATIVA = RUTA_ADMIN.replace(/^\//, '')

/** Construye una ruta del panel: rutaAdmin('servicios', String(id)). */
export function rutaAdmin(...partes: string[]): string {
  return [RUTA_ADMIN, ...partes.filter((parte) => parte !== '')].join('/')
}
