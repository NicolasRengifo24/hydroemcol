import { createBrowserRouter } from "react-router-dom";
import Layout from "./components/Layout";
import Admin from "./pages/Admin";
import AdminIndicadores from "./pages/AdminIndicadores";
import AdminServicios from "./pages/AdminServicios";
import AdminServicioDetalle from "./pages/AdminServicioDetalle";
import AdminLogin from "./pages/AdminLogin";
import AdminLayout from "./components/AdminLayout";
import RutaAdministrativaProtegida from "./components/RutaAdministrativaProtegida";
import Inicio from "./pages/Inicio";
import Nosotros from "./pages/Nosotros";
import Seguimiento from "./pages/Seguimiento";
import SeguimientoCodigo from "./pages/SeguimientoCodigo";
import SolicitarServicio from "./pages/SolicitarServicio";
import Soluciones from "./pages/Soluciones";

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
  { path: "admin/login", element: <AdminLogin /> },
  {
    element: <RutaAdministrativaProtegida />,
    children: [
      {
        element: <AdminLayout />,
        children: [
          { path: "admin", element: <Admin /> },
          { path: "admin/indicadores", element: <AdminIndicadores /> },
          { path: "admin/servicios", element: <AdminServicios /> },
          { path: "admin/servicios/:id", element: <AdminServicioDetalle /> },
        ],
      },
    ],
  },
]);
