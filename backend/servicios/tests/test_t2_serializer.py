from django.test import TestCase
from rest_framework.exceptions import ValidationError

from servicios.serializers import SolicitudPublicaSerializer


class T2SerializerTest(TestCase):
    def test_componentes_vacios_rechaza(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana@example.com",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [],
        }
        s = SolicitudPublicaSerializer(data=payload)
        self.assertFalse(s.is_valid())

    def test_minimo_valido(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana@example.com",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        s = SolicitudPublicaSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)

    def test_cantidad_mayor_igual_1(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana@example.com",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 0}],
        }
        s = SolicitudPublicaSerializer(data=payload)
        self.assertFalse(s.is_valid())

    def test_correo_normalizado(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": " Ana@Empresa.com ",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        s = SolicitudPublicaSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["correo_electronico"], "ana@empresa.com")
