import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import { LazyMotion, domAnimation } from 'framer-motion'
import { router } from './router'
import { SesionProvider } from './context/SesionContext'
import './index.css'

const queryClient = new QueryClient()

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
