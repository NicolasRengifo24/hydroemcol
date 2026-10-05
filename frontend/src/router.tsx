import { createBrowserRouter } from 'react-router-dom'
import Layout from './components/Layout'
import Admin from './pages/Admin'
import Contacto from './pages/Contacto'
import Inicio from './pages/Inicio'
import Nosotros from './pages/Nosotros'
import Seguimiento from './pages/Seguimiento'
import Servicios from './pages/Servicios'
import SolicitarServicio from './pages/SolicitarServicio'
import Soluciones from './pages/Soluciones'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Inicio /> },
      { path: 'nosotros', element: <Nosotros /> },
      { path: 'servicios', element: <Servicios /> },
      { path: 'soluciones', element: <Soluciones /> },
      { path: 'contacto', element: <Contacto /> },
      { path: 'solicitar', element: <SolicitarServicio /> },
      { path: 'seguimiento/:token', element: <Seguimiento /> },
      { path: 'admin', element: <Admin /> },
    ],
  },
])