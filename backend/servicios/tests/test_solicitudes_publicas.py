import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from servicios.models import (
    Cliente,
    Componente,
    EstadoServicio,
    Fotografia,
    Servicio,
    TipoFotografia,
)


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

    def test_whatsapp_solo_es_contacto_valido(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana3@example.com",
            "whatsapp": "+57 311-222-3344",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Cliente.objects.filter(whatsapp="3112223344").exists())

    def test_sin_contacto_telefonico_rechaza(self):
        payload = {
            "nombre_cliente": "Ana",
            "correo_electronico": "ana4@example.com",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("telefono", resp.data)

    def test_empresa_opcional_se_guarda(self):
        payload = {
            "nombre_cliente": "Ana",
            "empresa": "Servicios del Caribe S.A.S",
            "correo_electronico": "ana5@example.com",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Cliente.objects.filter(empresa="Servicios del Caribe S.A.S").exists())

    def _payload(self, **overrides):
        base = {
            "nombre_cliente": "Ana",
            "correo_electronico": f"ana{overrides.pop('_n', '')}@example.com",
            "telefono": "3001234567",
            "tipo_servicio": "PRUEBA",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }
        base.update(overrides)
        return base

    def test_descripcion_exactamente_500_ok(self):
        payload = self._payload(_n="500a", descripcion_problema="a" * 500)
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_descripcion_mas_de_500_rechaza(self):
        payload = self._payload(_n="500b", descripcion_problema="a" * 501)
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("descripcion_problema", resp.data)

    def test_componente_descripcion_mas_de_500_rechaza(self):
        payload = self._payload(
            _n="500c",
            componentes=[{"tipo": "BOMBA", "cantidad": 1, "descripcion": "a" * 501}],
        )
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("componentes", resp.data)

    def test_componente_descripcion_exactamente_500_ok(self):
        payload = self._payload(
            _n="500d",
            componentes=[{"tipo": "BOMBA", "cantidad": 1, "descripcion": "a" * 500}],
        )
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.data)

    def test_preferencias_guardadas(self):
        payload = self._payload(_n="pref1", entregar_en_banco=True, recoger=True)
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        servicio = Servicio.objects.get(codigo=resp.data["codigo"])
        self.assertTrue(servicio.entregar_en_banco)
        self.assertFalse(servicio.avisar_para_coordinar)
        self.assertTrue(servicio.recoger)

    def test_preferencias_por_defecto_vacias(self):
        payload = self._payload(_n="pref2")
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        servicio = Servicio.objects.get(codigo=resp.data["codigo"])
        self.assertFalse(servicio.entregar_en_banco)
        self.assertFalse(servicio.avisar_para_coordinar)
        self.assertFalse(servicio.recoger)

    def test_tipo_servicio_se_fuerza_a_prueba(self):
        payload = self._payload(_n="tipo1")
        payload["tipo_servicio"] = "DIAGNOSTICO"
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        servicio = Servicio.objects.get(codigo=resp.data["codigo"])
        self.assertEqual(servicio.tipo_servicio, "PRUEBA")

    def test_sin_tipo_servicio_en_payload(self):
        payload = self._payload(_n="tipo2")
        payload.pop("tipo_servicio", None)
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        servicio = Servicio.objects.get(codigo=resp.data["codigo"])
        self.assertEqual(servicio.tipo_servicio, "PRUEBA")

    def _crear_servicio(
        self,
        correo="ana@example.com",
        telefono="",
        whatsapp="",
        estado=EstadoServicio.SOLICITADO,
    ):
        cliente = Cliente.objects.create(email=correo, telefono=telefono, whatsapp=whatsapp)
        return Servicio.objects.create(
            cliente=cliente,
            tipo_servicio="PRUEBA",
            descripcion_solicitud="Solicitud previa",
            estado=estado,
        )

    def test_duplicado_avisa_con_409(self):
        self._crear_servicio(correo="dup@example.com")
        payload = self._payload(correo_electronico="dup@example.com")
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 409)
        self.assertTrue(resp.data["requiere_confirmacion"])
        self.assertNotIn("codigo", resp.data)

    def test_duplicado_sin_confirmar_no_crea(self):
        self._crear_servicio(correo="dup2@example.com")
        payload = self._payload(correo_electronico="dup2@example.com")
        self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(Servicio.objects.count(), 1)

    def test_duplicado_con_confirmar_crea(self):
        self._crear_servicio(correo="dup3@example.com")
        payload = self._payload(correo_electronico="dup3@example.com", confirmar=True)
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Servicio.objects.count(), 2)

    def test_servicio_cerrado_no_avisa(self):
        self._crear_servicio(
            correo="cerrado@example.com", estado=EstadoServicio.FINALIZADO
        )
        payload = self._payload(correo_electronico="cerrado@example.com")
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_duplicado_por_whatsapp(self):
        self._crear_servicio(correo="previo@example.com", whatsapp="3112223344")
        payload = self._payload(
            correo_electronico="nuevo@example.com",
            telefono="",
            whatsapp="+57 311-222-3344",
        )
        resp = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(resp.status_code, 409)
        self.assertTrue(resp.data["requiere_confirmacion"])

    def test_idempotencia_mismo_key_devuelve_misma(self):
        payload = self._payload(_n="idem1", idempotency_key="clave-abc")
        primero = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(primero.status_code, 201)

        segundo = self.client.post("/api/solicitudes/", payload, format="json")
        self.assertEqual(segundo.status_code, 200)
        self.assertEqual(segundo.data["codigo"], primero.data["codigo"])
        self.assertEqual(Servicio.objects.count(), 1)
        self.assertEqual(
            Servicio.objects.get(codigo=primero.data["codigo"]).idempotency_key,
            "clave-abc",
        )

    def test_idempotencia_por_header(self):
        payload = self._payload(_n="idem2")
        primero = self.client.post(
            "/api/solicitudes/", payload, format="json", HTTP_IDEMPOTENCY_KEY="clave-hdr"
        )
        self.assertEqual(primero.status_code, 201)

        segundo = self.client.post(
            "/api/solicitudes/", payload, format="json", HTTP_IDEMPOTENCY_KEY="clave-hdr"
        )
        self.assertEqual(segundo.status_code, 200)
        self.assertEqual(segundo.data["codigo"], primero.data["codigo"])
        self.assertEqual(Servicio.objects.count(), 1)

    def test_idempotencia_keys_distintas_crean_dos(self):
        primero = self.client.post(
            "/api/solicitudes/",
            self._payload(_n="idem3a", telefono="3000000001", idempotency_key="k-1"),
            format="json",
        )
        segundo = self.client.post(
            "/api/solicitudes/",
            self._payload(_n="idem3b", telefono="3000000002", idempotency_key="k-2"),
            format="json",
        )
        self.assertEqual(primero.status_code, 201)
        self.assertEqual(segundo.status_code, 201)
        self.assertEqual(Servicio.objects.count(), 2)


_MEDIA_TEST = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=_MEDIA_TEST)
class FotoSolicitudTest(TestCase):
    """Fotos de la solicitud pública: guardado (T11) y corrección (T12).

    - T11: una fotografía válida se guarda en media local y crea `Fotografia`.
    - T12: límite de 5 (RF-5.1/5.2), formatos JPG/JPEG/PNG (RF-5.3), tamaño
      máximo de 10 MB (criterio 4) y 0 fotos (RF-5.4).
    """

    def setUp(self):
        self.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_MEDIA_TEST, ignore_errors=True)

    def _payload(self):
        return {
            "nombre_cliente": "Ana",
            "correo_electronico": "foto@example.com",
            "telefono": "3001234567",
            "descripcion_problema": "Problema",
            "componentes": [{"tipo": "BOMBA", "cantidad": 1}],
        }

    @staticmethod
    def _imagen(nombre="bomba.png"):
        return SimpleUploadedFile(
            nombre,
            b"\x89PNG\r\n\x1a\ncontenido-simulado",
            content_type="image/png",
        )

    def _payload_multipart(self, fotografias):
        """Payload multipart: los componentes viajan con nombres indexados
        (`componentes[0]tipo`), como los enviaría un FormData real."""
        return {
            "nombre_cliente": "Ana",
            "correo_electronico": "foto@example.com",
            "telefono": "3001234567",
            "descripcion_problema": "Problema",
            "componentes[0]tipo": "BOMBA",
            "componentes[0]cantidad": "1",
            "fotografias": fotografias,
        }

    def test_foto_valida_crea_fotografia_en_media(self):
        resp = self.client.post(
            "/api/solicitudes/",
            self._payload_multipart([self._imagen()]),
            format="multipart",
        )

        self.assertEqual(resp.status_code, 201, resp.data)
        foto = Fotografia.objects.get(servicio__codigo=resp.data["codigo"])
        self.assertTrue(foto.url.startswith("/media/"))
        self.assertEqual(foto.tipo, TipoFotografia.RECEPCION)
        self.assertFalse(foto.visible_cliente)

    def test_solicitud_sin_fotos_ok(self):
        """RF-5.4: sin fotos la solicitud se registra y no hay `Fotografia`."""
        resp = self.client.post(
            "/api/solicitudes/", self._payload(), format="json"
        )
        self.assertEqual(resp.status_code, 201)
        self.assertFalse(
            Fotografia.objects.filter(
                servicio__codigo=resp.data["codigo"]
            ).exists()
        )

    def test_fotos_validas_crean_una_por_archivo(self):
        """Una `Fotografia` por archivo, con url/tipo/visibilidad de recepción."""
        imagenes = [
            self._imagen("bomba-uno.png"),
            self._imagen("bomba-dos.jpg"),
            self._imagen("bomba-tres.jpeg"),
        ]
        resp = self.client.post(
            "/api/solicitudes/",
            self._payload_multipart(imagenes),
            format="multipart",
        )

        self.assertEqual(resp.status_code, 201, resp.data)
        fotografias = Fotografia.objects.filter(
            servicio__codigo=resp.data["codigo"]
        )
        self.assertEqual(fotografias.count(), len(imagenes))
        for foto in fotografias:
            self.assertTrue(foto.url.startswith("/media/"))
            self.assertEqual(foto.tipo, TipoFotografia.RECEPCION)
            self.assertFalse(foto.visible_cliente)

    def test_cinco_fotos_ok(self):
        """RF-5.1/§6: exactamente cinco fotografías es un caso válido."""
        imagenes = [self._imagen(f"bomba-{i}.png") for i in range(5)]
        resp = self.client.post(
            "/api/solicitudes/",
            self._payload_multipart(imagenes),
            format="multipart",
        )

        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(
            Fotografia.objects.filter(
                servicio__codigo=resp.data["codigo"]
            ).count(),
            5,
        )

    def test_seis_fotos_rechaza_con_limite(self):
        """RF-5.2: una sexta fotografía se rechaza sin registrar la solicitud."""
        imagenes = [self._imagen(f"bomba-{i}.png") for i in range(6)]
        resp = self.client.post(
            "/api/solicitudes/",
            self._payload_multipart(imagenes),
            format="multipart",
        )

        self.assertEqual(resp.status_code, 400, resp.data)
        self.assertIn("fotografias", resp.data)
        self.assertIn("5 fotografías", str(resp.data))
        self.assertFalse(Servicio.objects.exists())
        self.assertFalse(Fotografia.objects.exists())

    def test_foto_formato_txt_rechaza(self):
        """RF-5.3: un formato no admitido (.txt) produce error claro y no crea."""
        archivo = SimpleUploadedFile(
            "notas.txt", b"contenido", content_type="text/plain"
        )
        resp = self.client.post(
            "/api/solicitudes/",
            self._payload_multipart([archivo]),
            format="multipart",
        )

        self.assertEqual(resp.status_code, 400, resp.data)
        self.assertIn("fotografias", resp.data)
        self.assertIn("Formato no admitido", str(resp.data))
        self.assertFalse(Servicio.objects.exists())
        self.assertFalse(Fotografia.objects.exists())

    def test_foto_formato_bmp_rechaza(self):
        """RF-5.3: un formato no admitido (.bmp) produce error claro y no crea."""
        archivo = SimpleUploadedFile(
            "imagen.bmp", b"BM-contenido", content_type="image/bmp"
        )
        resp = self.client.post(
            "/api/solicitudes/",
            self._payload_multipart([archivo]),
            format="multipart",
        )

        self.assertEqual(resp.status_code, 400, resp.data)
        self.assertIn("fotografias", resp.data)
        self.assertIn("Formato no admitido", str(resp.data))
        self.assertFalse(Servicio.objects.exists())
        self.assertFalse(Fotografia.objects.exists())

    def test_foto_mas_de_10mb_rechaza(self):
        """Criterio 4: una imagen de más de diez megabytes se rechaza."""
        grande = SimpleUploadedFile(
            "grande.png",
            b"x" * (10 * 1024 * 1024 + 1),
            content_type="image/png",
        )
        resp = self.client.post(
            "/api/solicitudes/",
            self._payload_multipart([grande]),
            format="multipart",
        )

        self.assertEqual(resp.status_code, 400, resp.data)
        self.assertIn("fotografias", resp.data)
        self.assertIn("10 MB", str(resp.data))
        self.assertFalse(Servicio.objects.exists())
        self.assertFalse(Fotografia.objects.exists())
