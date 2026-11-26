import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { obtenerVitrina } from '../services/vitrina'

export const clavesVitrina = {
  todas: ['vitrina'] as const,
  productos: (categoria: string | null) =>
    [...clavesVitrina.todas, 'productos', categoria ?? ''] as const,
}

// La vitrina usa React Query (patrón del panel) para carga, error y reintento.
// `staleTime: 0` mantiene la publicación inmediata; el reintento global de
// `main.tsx` no reintenta 4xx, así que un filtro inválido no se repite.
export function useVitrina(categoria: string | null) {
  return useQuery({
    queryKey: clavesVitrina.productos(categoria),
    queryFn: () => obtenerVitrina(categoria),
    staleTime: 0,
    // Conserva el catálogo de categorías mientras carga otro filtro. La página
    // no pinta los resultados anteriores: distingue `isPlaceholderData`.
    placeholderData: keepPreviousData,
  })
}
