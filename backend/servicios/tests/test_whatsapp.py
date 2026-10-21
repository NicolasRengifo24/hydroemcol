from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from servicios import validators
from servicios.mensajes import (
    construir_bloque_whatsapp,
    enlace_seguimiento,
    etiqueta_componente,
    texto_componente,
    texto_servicio,
)
from servicios.models import (
    AprobacionServicio,
    Cliente,
    Componente,
    Cotizacion,
    HistorialComponente,
    HistorialServicio,
    Servicio,
)
from usuarios.models import Usuario


def claves_contrato(valor):
    if isinstance(valor, dict):
        resultado = set(valor)
        for contenido in valor.values():
            resultado.update(claves_contrato(contenido))
        return resultado
    if isinstance(valor, list):
        resultado = set()
        for contenido in valor:
            resultado.update(claves_contrato(contenido))
        return resultado
    return set()


class ValidarCelularTest(SimpleTestCase):
    """CA-02 (validador), CL-01 y CL-02: tabla de entradas válidas e inválidas."""

    def test_numeros_validos_devuelven_solo_digitos(self):
        self.assertEqual(validators.validar_celular_colombiano('3001234567'), '3001234567')
        self.assertEqual(validators.validar_celular_colombiano('+57 300 123 4567'), '3001234567')
        self.assertEqual(validators.validar_celular_colombiano('57-300-123-4567'), '3001234567')

    def test_prefijo_57_con_parentesis_y_espacios(self):
        self.assertEqual(validators.validar_celular_colombiano('+57 (300) 123-4567'), '3001234567')
        self.assertEqual(validators.validar_celular_colombiano('57 300 123 4567'), '3001234567')

    def test_fijo_o_prefijo_de_otro_pais_se_rechaza(self):
        # CL-02: fijo bogotano de 10 dígitos que no empieza por 3
        self.assertIsNone(validators.validar_celular_colombiano('6011234567'))
        self.assertIsNone(validators.validar_celular_colombiano('+1 202 555 0134'))

    def test_longitudes_distintas_de_diez_se_rechazan(self):
        # 9 dígitos
        self.assertIsNone(validators.validar_celular_colombiano('300123456'))
        # 11 dígitos
        self.assertIsNone(validators.validar_celular_colombiano('30012345678'))
        # 12 dígitos sin prefijo 57 reconocible
        self.assertIsNone(validators.validar_celular_colombiano('300123456789'))

    def test_primer_digito_distinto_de_tres_se_rechaza(self):
        self.assertIsNone(validators.validar_celular_colombiano('4001234567'))
        self.assertIsNone(validators.validar_celular_colombiano('1300123456'))
        self.assertIsNone(validators.validar_celular_colombiano('2300123456'))

    def test_vacio_o_basura_se_rechaza(self):
        self.assertIsNone(validators.validar_celular_colombiano(''))
        self.assertIsNone(validators.validar_celular_colombiano('   '))
        self.assertIsNone(validators.validar_celular_colombiano('no es un numero'))


class SolicitudSinWhatsAppTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _payload(self, whatsapp=None):
        payload = {
            'nombre_cliente': 'Ana',
            'correo_electronico': 'sin-whatsapp@example.com',
            'telefono': '3001234567',
            'descripcion_problema': 'Problema',
            'componentes': [{'tipo': 'BOMBA', 'cantidad': 1}],
        }
        if whatsapp is not None:
            payload['whatsapp'] = whatsapp
        return payload

    def test_sin_whatsapp_rechaza_sin_crear_datos(self):
        respuesta = self.client.post('/api/solicitudes/', self._payload(), format='json')
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('whatsapp', respuesta.data)
        self.assertIn('Indica tu número de WhatsApp.', str(respuesta.data['whatsapp']))
        self.assertEqual(Cliente.objects.count(), 0)
        self.assertEqual(Servicio.objects.count(), 0)
        self.assertEqual(Componente.objects.count(), 0)

    def test_whatsapp_invalido_rechaza_sin_crear_datos(self):
        respuesta = self.client.post(
            '/api/solicitudes/', self._payload('6011234567'), format='json'
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('whatsapp', respuesta.data)
        self.assertIn('Escribe un celular colombiano', str(respuesta.data['whatsapp']))
        self.assertEqual(Cliente.objects.count(), 0)
        self.assertEqual(Servicio.objects.count(), 0)
        self.assertEqual(Componente.objects.count(), 0)


class NoSobrescribirTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _payload(self, correo):
        return {
            'nombre_cliente': 'Ana',
            'correo_electronico': correo,
            'telefono': '3001234567',
            'whatsapp': '3112223344',
            'descripcion_problema': 'Problema',
            'componentes': [{'tipo': 'BOMBA', 'cantidad': 1}],
            'confirmar': True,
        }

    def test_cliente_con_numero_a_conserva_a(self):
        cliente = Cliente.objects.create(
            nombre='Ana', email='con-numero@example.com', whatsapp='3001234567'
        )
        respuesta = self.client.post(
            '/api/solicitudes/', self._payload(cliente.email), format='json'
        )
        self.assertEqual(respuesta.status_code, 201)
        cliente.refresh_from_db()
        self.assertEqual(cliente.whatsapp, '3001234567')

    def test_cliente_con_whatsapp_antiguo_invalido_no_se_sobrescribe(self):
        cliente = Cliente.objects.create(
            nombre='Ana', email='numero-invalido@example.com', whatsapp='numero-invalido'
        )
        respuesta = self.client.post(
            '/api/solicitudes/', self._payload(cliente.email), format='json'
        )
        self.assertEqual(respuesta.status_code, 201)
        cliente.refresh_from_db()
        self.assertEqual(cliente.whatsapp, 'numero-invalido')

    def test_cliente_sin_numero_guarda_b(self):
        cliente = Cliente.objects.create(
            nombre='Ana', email='sin-numero@example.com', whatsapp=''
        )
        respuesta = self.client.post(
            '/api/solicitudes/', self._payload(cliente.email), format='json'
        )
        self.assertEqual(respuesta.status_code, 201)
        cliente.refresh_from_db()
        self.assertEqual(cliente.whatsapp, '3112223344')


class ContenidoMensajeTest(SimpleTestCase):
    """CA-12: textos exactos, enlace y privacidad del mensaje preparado."""

    def setUp(self):
        self.servicio = {
            'id': 41,
            'codigo': 'SRV-2026-00009',
            'estado': 'EN_CURSO',
            'activo': True,
            'token_seguimiento': 'token-privado',
            'observaciones_internas': 'no debe salir',
        }
        self.componentes = [
            {
                'id': 12,
                'tipo': 'Bomba hidráulica',
                'referencia': 'REF-77',
                'estado': 'EN_PRUEBAS',
                'motivo_finalizacion': '',
                'motivo_bloqueo': 'bloqueo interno',
                'usuario': 'admin-interno',
            },
            {
                'id': 13,
                'tipo': 'Cilindro',
                'referencia': '',
                'estado': 'RECHAZADO',
                'motivo_finalizacion': 'Motivo visible',
            },
        ]

    def test_textos_aprobados_y_enlace_son_exactos(self):
        enlace = 'https://ejemplo.test/seguimiento/token-privado'
        self.assertEqual(
            enlace_seguimiento('https://ejemplo.test///', 'token-privado'),
            enlace,
        )
        self.assertEqual(
            texto_servicio('SOLICITADO', 'SRV-2026-00009', enlace),
            'Hidroemcol: recibimos su solicitud SRV-2026-00009. '
            'Siga el avance en: https://ejemplo.test/seguimiento/token-privado',
        )
        self.assertEqual(
            texto_servicio('EN_CURSO', 'SRV-2026-00009', enlace),
            'Hidroemcol: su servicio SRV-2026-00009 está en curso. '
            'Siga el avance en: https://ejemplo.test/seguimiento/token-privado',
        )
        textos_componentes = {
            'PENDIENTE': (
                'Hidroemcol: el componente Bomba hidráulica (REF-77) del servicio '
                'SRV-2026-00009 fue recibido.'
            ),
            'EN_REVISION': (
                'Hidroemcol: el componente Bomba hidráulica (REF-77) del servicio '
                'SRV-2026-00009 está en revisión.'
            ),
            'COTIZANDO': (
                'Hidroemcol: estamos preparando la cotización de '
                'Bomba hidráulica (REF-77) (servicio SRV-2026-00009).'
            ),
            'ESPERANDO_APROBACION': (
                'Hidroemcol: Bomba hidráulica (REF-77) (servicio SRV-2026-00009) '
                'espera su aprobación. Revise la cotización en: '
                'https://ejemplo.test/seguimiento/token-privado'
            ),
            'OPERARIO_TRABAJANDO': (
                'Hidroemcol: iniciamos el trabajo en Bomba hidráulica (REF-77) '
                '(servicio SRV-2026-00009).'
            ),
            'EN_PRUEBAS': (
                'Hidroemcol: Bomba hidráulica (REF-77) (servicio SRV-2026-00009) '
                'está en pruebas.'
            ),
            'LISTO_PARA_ENTREGA': (
                'Hidroemcol: Bomba hidráulica (REF-77) (servicio SRV-2026-00009) '
                'está listo para entregar.'
            ),
            'RECHAZADO': (
                'Hidroemcol: Bomba hidráulica (REF-77) (servicio SRV-2026-00009) '
                'fue rechazado. Motivo: Motivo visible. Detalle: '
                'https://ejemplo.test/seguimiento/token-privado'
            ),
        }
        for estado, texto_aprobado in textos_componentes.items():
            with self.subTest(estado=estado):
                motivo = 'Motivo visible' if estado == 'RECHAZADO' else ''
                self.assertEqual(
                    texto_componente(
                        estado, 'Bomba hidráulica (REF-77)',
                        'SRV-2026-00009', enlace, motivo,
                    ),
                    texto_aprobado,
                )
        self.assertEqual(etiqueta_componente('Cilindro', ''), 'Cilindro')

    def test_estados_de_servicio_cerrados_no_se_preparan(self):
        enlace = 'https://ejemplo.test/seguimiento/token-privado'
        self.assertIsNone(texto_servicio('FINALIZADO', 'SRV-2026-00009', enlace))
        self.assertIsNone(texto_servicio('CANCELADO', 'SRV-2026-00009', enlace))

    def test_base_invalida_no_produce_enlace(self):
        self.assertIsNone(enlace_seguimiento('', 'token'))
        self.assertIsNone(enlace_seguimiento('ejemplo.test', 'token'))
        self.assertIsNone(texto_servicio('EN_CURSO', 'SRV-1', None))

    def test_motivo_solo_aparece_en_rechazado(self):
        enlace = enlace_seguimiento('https://ejemplo.test', 'token-privado')
        rechazado = texto_componente(
            'RECHAZADO', 'Cilindro', 'SRV-2026-00009', enlace, 'Motivo visible'
        )
        listo = texto_componente(
            'LISTO_PARA_ENTREGA', 'Cilindro', 'SRV-2026-00009', enlace,
            'Motivo que no debe salir',
        )
        self.assertIn('Motivo visible', rechazado)
        self.assertNotIn('Motivo que no debe salir', listo)
        self.assertIsNone(
            texto_componente(
                'RECHAZADO', 'Cilindro', 'SRV-1', enlace, '',
            )
        )

    def test_bloque_no_expone_datos_internos_ni_identificadores(self):
        bloque = construir_bloque_whatsapp(
            self.servicio, self.componentes, 'https://ejemplo.test', '3001234567'
        )
        contrato = str(bloque)
        textos = ' '.join(str(mensaje) for mensaje in bloque['mensajes'] if mensaje['texto'])
        for clave in ('componente_id', 'servicio_id', 'id'):
            self.assertNotIn(clave, claves_contrato(bloque))
        valores = []

        def recoger_valores(valor):
            if isinstance(valor, dict):
                for contenido in valor.values():
                    recoger_valores(contenido)
            elif isinstance(valor, list):
                for contenido in valor:
                    recoger_valores(contenido)
            else:
                valores.append(valor)

        recoger_valores(bloque)
        for identificador in (41, 12, 13):
            self.assertNotIn(identificador, valores)
        self.assertNotIn('no debe salir', textos)
        self.assertNotIn('bloqueo interno', textos)
        self.assertNotIn('admin-interno', textos)
        self.assertIn('Motivo visible', textos)
        self.assertEqual(bloque['numero_destino'], '573001234567')
        self.assertEqual(bloque['mensajes'][0]['clave'], 'servicio')
        self.assertEqual(bloque['mensajes'][1]['clave'], 'componente-en_pruebas-0')
        self.assertEqual(bloque['mensajes'][2]['clave'], 'componente-rechazado-1')

    def test_estados_sin_enlace_se_preparan_sin_dominio(self):
        servicio = {**self.servicio, 'estado': 'EN_CURSO'}
        componentes = [{**self.componentes[0], 'estado': 'EN_REVISION'}]
        bloque = construir_bloque_whatsapp(
            servicio, componentes, '', '3001234567'
        )
        self.assertEqual(len(bloque['mensajes']), 2)
        self.assertIsNone(bloque['mensajes'][0]['texto'])
        self.assertEqual(
            bloque['mensajes'][1]['texto'],
            'Hidroemcol: el componente Bomba hidráulica (REF-77) del servicio '
            'SRV-2026-00009 está en revisión.',
        )


class WhatsAppVistaBase:
    def crear_servicio(self, whatsapp='3001234567'):
        cliente = Cliente.objects.create(nombre='Cliente', whatsapp=whatsapp)
        servicio = Servicio.objects.create(
            cliente=cliente, descripcion_solicitud='Prueba', estado='EN_CURSO',
        )
        componente = Componente.objects.create(
            servicio=servicio, tipo='Bomba hidráulica', referencia='REF-77',
            estado='EN_PRUEBAS',
        )
        return servicio, componente

    def crear_administrativo(self, activo=True, rol='ADMINISTRATIVO'):
        return Usuario.objects.create_user(
            username=f'admin-{Usuario.objects.count()}',
            password='clave-segura', is_active=activo, rol=rol,
        )


@override_settings(SEGUIMIENTO_BASE_URL='https://ejemplo.test')
class WhatsAppPermisosTest(WhatsAppVistaBase, TestCase):
    def setUp(self):
        self.cliente_sin_rol = self.crear_administrativo(rol='OTRO')
        self.usuario_inactivo = self.crear_administrativo(activo=False)
        self.administrativo = self.crear_administrativo()
        self.servicio, _ = self.crear_servicio()
        self.url = f'/api/servicios/{self.servicio.pk}/whatsapp/'
        self.cliente_api = APIClient()

    def test_sin_autenticacion_no_recibe_datos(self):
        respuesta = self.cliente_api.get(self.url)
        self.assertIn(respuesta.status_code, (401, 403))
        self.assertNotIn('mensajes', respuesta.data)

    def test_usuario_sin_rol_no_recibe_datos(self):
        self.cliente_api.force_authenticate(self.cliente_sin_rol)
        respuesta = self.cliente_api.get(self.url)
        self.assertEqual(respuesta.status_code, 403)
        self.assertNotIn('mensajes', respuesta.data)

    def test_cuenta_inactiva_no_recibe_datos(self):
        self.cliente_api.force_authenticate(self.usuario_inactivo)
        respuesta = self.cliente_api.get(self.url)
        self.assertEqual(respuesta.status_code, 403)
        self.assertNotIn('mensajes', respuesta.data)

    def test_administrativo_recibe_el_contrato(self):
        self.cliente_api.force_authenticate(self.administrativo)
        respuesta = self.cliente_api.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['codigo'], self.servicio.codigo)
        self.assertEqual(respuesta.data['numero_destino'], '573001234567')
        self.assertEqual(len(respuesta.data['mensajes']), 2)
        contrato = str(respuesta.data)
        for clave in ('componente_id', 'servicio_id', 'id'):
            self.assertNotIn(clave, claves_contrato(respuesta.data))
        valores = []

        def recoger_valores(valor):
            if isinstance(valor, dict):
                for contenido in valor.values():
                    recoger_valores(contenido)
            elif isinstance(valor, list):
                for contenido in valor:
                    recoger_valores(contenido)
            else:
                valores.append(valor)

        recoger_valores(respuesta.data)
        self.assertNotIn(self.servicio.pk, valores)


@override_settings(SEGUIMIENTO_BASE_URL='https://ejemplo.test')
class WhatsAppSoloLecturaTest(WhatsAppVistaBase, TestCase):
    def setUp(self):
        self.administrativo = self.crear_administrativo()
        self.servicio, _ = self.crear_servicio()
        self.url = f'/api/servicios/{self.servicio.pk}/whatsapp/'
        self.cliente_api = APIClient()
        self.cliente_api.force_authenticate(self.administrativo)

    def test_get_no_escribe_filas_y_post_es_405(self):
        conteos_antes = (
            Servicio.objects.count(), Componente.objects.count(),
            Cotizacion.objects.count(), AprobacionServicio.objects.count(),
            HistorialServicio.objects.count(), HistorialComponente.objects.count(),
        )
        respuesta = self.cliente_api.get(self.url)
        conteos_despues = (
            Servicio.objects.count(), Componente.objects.count(),
            Cotizacion.objects.count(), AprobacionServicio.objects.count(),
            HistorialServicio.objects.count(), HistorialComponente.objects.count(),
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(conteos_antes, conteos_despues)
        self.assertEqual(self.cliente_api.post(self.url, {}, format='json').status_code, 405)

    def test_servicio_inexistente_responde_404(self):
        respuesta = self.cliente_api.get('/api/servicios/999999/whatsapp/')
        self.assertEqual(respuesta.status_code, 404)

    def test_cerrado_inactivo_y_sin_numero_no_preparan_mensajes(self):
        for cambios, aviso in (
            ({'estado': 'FINALIZADO'}, 'cerrado'),
            ({'activo': False}, 'desactivado'),
        ):
            servicio, _ = self.crear_servicio()
            for campo, valor in cambios.items():
                setattr(servicio, campo, valor)
            servicio.save(update_fields=list(cambios))
            respuesta = self.cliente_api.get(f'/api/servicios/{servicio.pk}/whatsapp/')
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(respuesta.data['mensajes'], [])
            self.assertIn(aviso, respuesta.data['aviso'])

        servicio, _ = self.crear_servicio(whatsapp='no-valido')
        respuesta = self.cliente_api.get(f'/api/servicios/{servicio.pk}/whatsapp/')
        self.assertEqual(respuesta.data['mensajes'], [])
        self.assertIn('no tiene un número', respuesta.data['aviso'])


@override_settings(SEGUIMIENTO_BASE_URL='https://ejemplo.test')
class WhatsAppTrasRechazoTest(WhatsAppVistaBase, TestCase):
    def setUp(self):
        self.administrativo = self.crear_administrativo()
        self.servicio, self.componente = self.crear_servicio()
        self.url = f'/api/servicios/{self.servicio.pk}/whatsapp/'
        self.estado_url = (
            f'/api/servicios/{self.servicio.pk}/componentes/'
            f'{self.componente.pk}/estado/'
        )
        self.cliente_api = APIClient()
        self.cliente_api.force_authenticate(self.administrativo)

    def test_rechazo_y_mismo_estado_no_cambian_historial_ni_texto(self):
        antes = self.cliente_api.get(self.url).data
        historial_antes = (
            HistorialServicio.objects.count(), HistorialComponente.objects.count(),
        )
        rechazo = self.cliente_api.post(
            self.estado_url, {'estado': 'OPERARIO_TRABAJANDO'},
            format='json',
        )
        self.assertEqual(rechazo.status_code, 409)
        mismo_estado = self.cliente_api.post(
            self.estado_url, {'estado': 'EN_PRUEBAS'}, format='json',
        )
        self.assertEqual(mismo_estado.status_code, 200)
        despues = self.cliente_api.get(self.url).data
        self.assertEqual(historial_antes, (
            HistorialServicio.objects.count(), HistorialComponente.objects.count(),
        ))
        self.assertEqual(
            [mensaje['texto'] for mensaje in antes['mensajes']],
            [mensaje['texto'] for mensaje in despues['mensajes']],
        )
