import { Navigate, createBrowserRouter } from "react-router-dom";
import Layout from "./components/Layout";
import Admin from "./pages/Admin";
import AdminIndicadores from "./pages/AdminIndicadores";
import AdminServicios from "./pages/AdminServicios";
import AdminServicioDetalle from "./pages/AdminServicioDetalle";
import AdminLogin from "./pages/AdminLogin";
import AdminLayout from "./components/AdminLayout";
import RutaAdministrativaProtegida from "./components/RutaAdministrativaProtegida";
import Inicio from "./pages/Inicio";
import NoEncontrada from "./pages/NoEncontrada";
import Nosotros from "./pages/Nosotros";
import Seguimiento from "./pages/Seguimiento";
import SeguimientoCodigo from "./pages/SeguimientoCodigo";
import SolicitarServicio from "./pages/SolicitarServicio";
import Soluciones from "./pages/Soluciones";
import { RUTA_ADMIN_RELATIVA } from "./config/rutasAdmin";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Inicio /> },
      { path: "nosotros", element: <Nosotros /> },
      { path: "soluciones", element: <Soluciones /> },
      { path: "solicitar", element: <SolicitarServicio /> },
      { path: "seguimiento", element: <SeguimientoCodigo /> },
      { path: "seguimiento/:token", element: <Seguimiento /> },
    ],
  },
  { path: `${RUTA_ADMIN_RELATIVA}/login`, element: <AdminLogin /> },
  {
    element: <RutaAdministrativaProtegida />,
    children: [
      {
        element: <AdminLayout />,
        children: [
          { path: RUTA_ADMIN_RELATIVA, element: <Admin /> },
          { path: `${RUTA_ADMIN_RELATIVA}/indicadores`, element: <AdminIndicadores /> },
          { path: `${RUTA_ADMIN_RELATIVA}/servicios`, element: <AdminServicios /> },
          { path: `${RUTA_ADMIN_RELATIVA}/servicios/:id`, element: <AdminServicioDetalle /> },
        ],
      },
    ],
  },
  { path: "admin", element: <Navigate to="/" replace /> },
  { path: "admin/*", element: <Navigate to="/" replace /> },
  { path: "*", element: <NoEncontrada /> },
]);
