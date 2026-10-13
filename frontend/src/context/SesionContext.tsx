import { useSyncExternalStore } from 'react'
import { obtenerEstadoSesion, suscribirseSesion, type EstadoSesion } from '../services/api'
import { SesionContext } from './SesionContextValue'

export function SesionProvider({ children }: { children: React.ReactNode }) {
  const estado = useSyncExternalStore(suscribirseSesion, obtenerEstadoSesion, (): EstadoSesion => 'anonima')

  return <SesionContext.Provider value={estado}>{children}</SesionContext.Provider>
}
