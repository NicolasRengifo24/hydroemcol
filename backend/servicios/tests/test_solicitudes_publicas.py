from django.test import TestCase
from rest_framework.test import APIClient
from servicios.models import Cliente, Servicio, Componente
from servicios import estados


class SolicitudesPublicasTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_crear_solicitud_minima_ok(self):
        payload = {
            "nombre_cliente": "Ana Pérez",
            "correo_electronico": "ana@example.com",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema de prueba",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("codigo", resp.data)
        self.assertIn("enlace_seguimiento", resp.data)
        self.assertTrue(Servicio.objects.filter(codigo=resp.data["codigo"]).exists())

    def test_rechaza_sin_componentes(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana@example.com",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_cantidad_menor_a_1_invalida(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana@example.com",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 0}],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_correo_normalizado(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": " Ana@Empresa.COM ",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Cliente.objects.filter(email="ana@empresa.com").exists())

    def test_telefono_normalizado(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana2@example.com",
            "telefono": "+57 300-123-4567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Cliente.objects.filter(telefono="3001234567").exists())
