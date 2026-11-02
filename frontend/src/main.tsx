import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import { LazyMotion, domAnimation } from 'framer-motion'
import { router } from './router'
import { SesionProvider } from './context/SesionContext'
import {
  esFalloDeInfraestructura,
  marcarNoDisponible,
} from './services/disponibilidad'
import './index.css'

function debeReintentar(intento: number, error: unknown): boolean {
  const status =
    typeof error === 'object' && error !== null && 'status' in error
      ? (error as { status?: unknown }).status
      : undefined

  // Los errores de validación, sesión o permisos no mejoran al reintentar.
  if (typeof status === 'number' && status >= 400 && status < 500) {
    return false
  }

  return intento < 1
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: debeReintentar,
    },
    mutations: {
      retry: 0,
    },
  },
  queryCache: new QueryCache({
    onError: (error) => {
      if (esFalloDeInfraestructura(error)) marcarNoDisponible()
    },
  }),
  mutationCache: new MutationCache({
    onError: (error) => {
      if (esFalloDeInfraestructura(error)) marcarNoDisponible()
    },
  }),
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <LazyMotion features={domAnimation} strict>
      <QueryClientProvider client={queryClient}>
        <SesionProvider>
          <RouterProvider router={router} />
        </SesionProvider>
      </QueryClientProvider>
    </LazyMotion>
  </StrictMode>,
)
