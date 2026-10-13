import { createContext } from 'react'
import type { EstadoSesion } from '../services/api'

export const SesionContext = createContext<EstadoSesion>('anonima')
