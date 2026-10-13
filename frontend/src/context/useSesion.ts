import { useContext } from 'react'
import type { EstadoSesion } from '../services/api'
import { SesionContext } from './SesionContextValue'

export function useSesion(): EstadoSesion {
  return useContext(SesionContext)
}
