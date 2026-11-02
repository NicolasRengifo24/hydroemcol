import { useSyncExternalStore } from 'react'
import {
  obtenerFotoDisponibilidad,
  suscribirseDisponibilidad,
  type FotoDisponibilidad,
} from '../services/disponibilidad'

export function useDisponibilidadApi(): FotoDisponibilidad {
  return useSyncExternalStore(
    suscribirseDisponibilidad,
    obtenerFotoDisponibilidad,
    obtenerFotoDisponibilidad,
  )
}
