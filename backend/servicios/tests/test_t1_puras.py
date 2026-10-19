from django.test import SimpleTestCase
from servicios import validators, reglas
from servicios.models import EstadoServicio


class T1ValidatorsTest(SimpleTestCase):
    def test_normalizar_correo_strip_lower(self):
        self.assertEqual(validators.normalizar_correo('  Juan@Empresa.COM  '), 'juan@empresa.com')
        self.assertEqual(validators.normalizar_correo('test@example.org'), 'test@example.org')
        self.assertEqual(validators.normalizar_correo(''), '')

    def test_normalizar_telefono_limpia_y_normaliza(self):
        self.assertEqual(validators.normalizar_telefono('+57 300-123-4567'), '3001234567')
        self.assertEqual(validators.normalizar_telefono('(310) 555-1212'), '3105551212')
        self.assertEqual(validators.normalizar_telefono('3001234567'), '3001234567')
        self.assertEqual(validators.normalizar_telefono(''), '')
        self.assertEqual(validators.normalizar_telefono('57 300 123 4567'), '3001234567')
        self.assertEqual(validators.normalizar_telefono('+57(300)123-4567'), '3001234567')


class T1ReglasTest(SimpleTestCase):
    def test_estados_cerrados_definidos(self):
        cerrados = reglas.estados_cerrados()
        self.assertIn(EstadoServicio.FINALIZADO, cerrados)
        self.assertIn(EstadoServicio.CANCELADO, cerrados)

    def test_tiene_solicitud_en_curso_sin_datos_no_consulta_bd(self):
        hoy = {'componentes': []}
        resultado = reglas.tiene_solicitud_en_curso(hoy)
        self.assertIsInstance(resultado, bool)
        self.assertFalse(resultado)
