from django.test import TestCase
from rest_framework.test import APIClient
from servicios import estados


class T3ViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_post_solicitud_publica_crea_servicio(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana@example.com",
            "telefono": "3001234567",
            "whatsapp": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("codigo", resp.data)
        self.assertIn("enlace_seguimiento", resp.data)

    def test_post_solicitud_publica_sin_auth_permite(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana@example.com",
            "telefono": "3001234567",
            "whatsapp": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
