"""Contrato y seguridad de la autenticación administrativa (spec 004)."""

from datetime import timedelta
import logging

from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario


@override_settings(
    SECURE_SSL_REDIRECT=False,
    AUTH_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
)
class AutenticacionContratoTests(TestCase):
    """Comprueba el contrato HTTP sin usar un runner o dependencia adicional."""

    def setUp(self):
        cache.clear()
        self.cliente = Client(enforce_csrf_checks=True)
        self.usuario = Usuario.objects.create_user(
            username='administrador', password='Password-segura-123',
            rol=Usuario.Roles.ADMINISTRATIVO,
        )
        self.ip = '10.20.30.40'

    def csrf(self):
        respuesta = self.cliente.get('/api/csrf/', REMOTE_ADDR=self.ip)
        self.assertEqual(respuesta.status_code, 200)
        return self.cliente.cookies['csrftoken'].value

    def post_auth(self, ruta, datos=None, csrf=None, **extra):
        return self.cliente.post(
            ruta,
            data=datos or {},
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf or self.csrf(),
            REMOTE_ADDR=self.ip,
            **extra,
        )

    def iniciar_sesion(self, password='Password-segura-123'):
        return self.post_auth(
            '/api/login/',
            {'username': self.usuario.username, 'password': password},
        )

    def refresh_cookie(self, respuesta):
        return respuesta.cookies['refresh_token'].value

    def instalar_refresh(self, token):
        self.cliente.cookies['refresh_token'] = token

    def test_csrf_publico_establece_cookie_y_no_entrega_tokens(self):
        respuesta = self.cliente.get('/api/csrf/', REMOTE_ADDR=self.ip)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {'detail': 'CSRF listo'})
        self.assertIn('csrftoken', respuesta.cookies)
        self.assertNotIn('access', respuesta.json())
        self.assertNotIn('refresh_token', respuesta.json())

    def test_login_exitoso_solo_entrega_access_y_cookie_refresh(self):
        respuesta = self.iniciar_sesion()

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()['access'])
        self.assertNotIn('refresh', respuesta.json())
        self.assertNotIn('refresh_token', respuesta.json())
        self.assertIn('refresh_token', respuesta.cookies)
        self.assertNotIn('access', self.cliente.cookies)

    def test_login_rechaza_rol_incorrecto_e_inactivo_con_mensaje_generico(self):
        self.usuario.rol = 'OTRO'
        self.usuario.save(update_fields=['rol'])
        rol = self.iniciar_sesion()
        self.assertEqual(rol.status_code, 401)
        self.assertEqual(rol.json(), {'detail': 'Usuario o contraseña incorrectos'})

        self.usuario.rol = Usuario.Roles.ADMINISTRATIVO
        self.usuario.is_active = False
        self.usuario.save(update_fields=['rol', 'is_active'])
        inactivo = self.iniciar_sesion()
        self.assertEqual(inactivo.status_code, 401)
        self.assertEqual(inactivo.json(), {'detail': 'Usuario o contraseña incorrectos'})

    def test_credenciales_invalidas_inexistentes_e_inactivos_son_genericos(self):
        casos = [
            ('administrador', 'incorrecta'),
            ('no-existe', 'incorrecta'),
        ]
        for username, password in casos:
            respuesta = self.post_auth(
                '/api/login/', {'username': username, 'password': password},
            )
            self.assertEqual(respuesta.status_code, 401)
            self.assertEqual(respuesta.json(), {'detail': 'Usuario o contraseña incorrectos'})

        self.usuario.is_active = False
        self.usuario.save(update_fields=['is_active'])
        respuesta = self.iniciar_sesion()
        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(respuesta.json(), {'detail': 'Usuario o contraseña incorrectos'})

    def test_cookie_refresh_tiene_atributos_contractuales(self):
        cookie = self.iniciar_sesion().cookies['refresh_token']

        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['path'], '/api/')
        self.assertEqual(cookie['samesite'], 'Lax')
        self.assertFalse(cookie['secure'])
        self.assertEqual(cookie['domain'], '')
        self.assertEqual(int(cookie['max-age']), 86400)

    @override_settings(AUTH_COOKIE_SECURE=True)
    def test_cookie_refresh_es_secure_en_produccion(self):
        cookie = self.iniciar_sesion().cookies['refresh_token']
        self.assertTrue(cookie['secure'])
        self.assertEqual(cookie['samesite'], 'Lax')

    def test_csrf_ausente_o_invalido_protege_login_refresh_y_logout(self):
        for ruta, datos in (
            ('/api/login/', {'username': 'administrador', 'password': 'Password-segura-123'}),
            ('/api/refresh/', {}),
            ('/api/logout/', {}),
        ):
            ausente = self.cliente.post(
                ruta, data=datos, content_type='application/json', REMOTE_ADDR=self.ip,
            )
            self.assertEqual(ausente.status_code, 403, ruta)
            invalido = self.cliente.post(
                ruta, data=datos, content_type='application/json',
                HTTP_X_CSRFTOKEN='invalido', REMOTE_ADDR=self.ip,
            )
            self.assertEqual(invalido.status_code, 403, ruta)

    def test_refresh_valido_rota_blacklistea_y_no_acepta_el_anterior(self):
        login = self.iniciar_sesion()
        anterior = self.refresh_cookie(login)
        anterior_jti = RefreshToken(anterior)['jti']
        self.instalar_refresh(anterior)

        respuesta = self.post_auth('/api/refresh/')
        nuevo = self.refresh_cookie(respuesta)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()['access'])
        self.assertNotEqual(anterior, nuevo)
        self.assertTrue(
            BlacklistedToken.objects.filter(token__jti=anterior_jti).exists()
        )

        self.instalar_refresh(anterior)
        reutilizado = self.post_auth('/api/refresh/')
        self.assertEqual(reutilizado.status_code, 401)
        self.assertNotIn('access', reutilizado.json() if reutilizado.content else {})

    def test_refresh_expirado_devuelve_401(self):
        token = RefreshToken.for_user(self.usuario)
        token['exp'] = int((timezone.now() - timedelta(seconds=1)).timestamp())
        self.instalar_refresh(str(token))

        respuesta = self.post_auth('/api/refresh/')

        self.assertEqual(respuesta.status_code, 401)

    def test_reutilizacion_revoca_todos_los_refresh_vigentes_del_usuario(self):
        primero = self.iniciar_sesion()
        token_primero = self.refresh_cookie(primero)
        segundo = self.iniciar_sesion()
        token_segundo = self.refresh_cookie(segundo)

        self.instalar_refresh(token_primero)
        rotado = self.post_auth('/api/refresh/')
        token_rotado = self.refresh_cookie(rotado)
        self.instalar_refresh(token_primero)
        self.assertEqual(self.post_auth('/api/refresh/').status_code, 401)

        for token in (token_segundo, token_rotado):
            self.instalar_refresh(token)
            self.assertEqual(self.post_auth('/api/refresh/').status_code, 401)

    def test_logout_es_idempotente_204_y_elimina_cookie(self):
        login = self.iniciar_sesion()
        self.instalar_refresh(self.refresh_cookie(login))
        primera = self.post_auth('/api/logout/')
        segunda = self.post_auth('/api/logout/')

        for respuesta in (primera, segunda):
            self.assertEqual(respuesta.status_code, 204)
            cookie = respuesta.cookies['refresh_token']
            self.assertEqual(cookie['path'], '/api/')
            self.assertEqual(cookie['samesite'], 'Lax')
            self.assertEqual(cookie['max-age'], 0)

    def test_throttling_es_por_ip_y_solo_cuenta_fallos_de_credenciales(self):
        for _ in range(5):
            self.assertEqual(self.iniciar_sesion('incorrecta').status_code, 401)
        self.assertEqual(self.iniciar_sesion('incorrecta').status_code, 429)

        cache.clear()
        self.usuario.rol = 'OTRO'
        self.usuario.save(update_fields=['rol'])
        for _ in range(6):
            self.assertEqual(self.iniciar_sesion().status_code, 401)

        cache.clear()
        self.usuario.rol = Usuario.Roles.ADMINISTRATIVO
        self.usuario.save(update_fields=['rol'])
        for _ in range(5):
            self.assertEqual(self.iniciar_sesion('incorrecta').status_code, 401)
        self.assertEqual(
            self.cliente.post(
                '/api/login/',
                data={'username': '', 'password': ''},
                content_type='application/json',
                HTTP_X_CSRFTOKEN=self.csrf(), REMOTE_ADDR=self.ip,
            ).status_code,
            400,
        )
        self.assertEqual(self.iniciar_sesion('incorrecta').status_code, 429)

        cache.clear()
        self.assertEqual(self.iniciar_sesion('incorrecta').status_code, 401)
        self.assertEqual(
            self.cliente.post(
                '/api/login/',
                data={'username': 'administrador', 'password': 'incorrecta'},
                content_type='application/json',
                HTTP_X_CSRFTOKEN=self.csrf(), REMOTE_ADDR='10.20.30.41',
            ).status_code,
            401,
        )

    def test_throttling_no_cuenta_exito_forma_invalida_ni_csrf(self):
        cache.clear()
        for _ in range(4):
            self.assertEqual(self.iniciar_sesion('incorrecta').status_code, 401)
        self.assertEqual(self.iniciar_sesion().status_code, 200)

        for _ in range(5):
            self.assertEqual(self.iniciar_sesion('incorrecta').status_code, 401)
        self.assertEqual(
            self.cliente.post(
                '/api/login/', data={}, content_type='application/json',
                HTTP_X_CSRFTOKEN=self.csrf(), REMOTE_ADDR=self.ip,
            ).status_code,
            400,
        )
        self.assertEqual(
            self.cliente.post(
                '/api/login/',
                data={'username': 'administrador', 'password': 'incorrecta'},
                content_type='application/json', REMOTE_ADDR=self.ip,
            ).status_code,
            403,
        )
        self.assertEqual(self.iniciar_sesion('incorrecta').status_code, 429)

    def test_logs_no_contienen_secretos(self):
        password = 'Password-segura-123'
        access = self.iniciar_sesion().json()['access']
        csrf = self.csrf()
        self.cliente.cookies['refresh_token'] = 'cookie-privada'
        registros = []

        class Capturador(logging.Handler):
            def emit(self, registro):
                registros.append(registro.getMessage())

        capturador = Capturador()
        logger = logging.getLogger('usuarios.seguridad')
        logger.addHandler(capturador)
        try:
            respuesta = self.cliente.post(
                '/api/login/',
                data={'username': self.usuario.username, 'password': password},
                content_type='application/json', HTTP_X_CSRFTOKEN=csrf,
                HTTP_AUTHORIZATION=f'Bearer {access}',
                REMOTE_ADDR=self.ip, HTTP_USER_AGENT='navegador-de-prueba',
            )
        finally:
            logger.removeHandler(capturador)

        texto = '\n'.join(registros)
        self.assertEqual(respuesta.status_code, 200)
        for secreto in (password, access, 'cookie-privada', csrf):
            self.assertNotIn(secreto, texto)
        self.assertNotIn('Authorization', texto)
        self.assertNotIn('CSRF', texto)

    def test_endpoints_administrativos_requieren_jwt(self):
        anonima = self.cliente.get('/api/servicios/', REMOTE_ADDR=self.ip)
        self.assertEqual(anonima.status_code, 401)

        login = self.iniciar_sesion()
        autorizada = self.cliente.get(
            '/api/servicios/',
            HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}",
            REMOTE_ADDR=self.ip,
        )
        self.assertEqual(autorizada.status_code, 200)
