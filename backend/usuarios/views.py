import hashlib
import logging
from collections.abc import Mapping

from django.contrib.auth import authenticate
from django.core.cache import cache
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenBackendExpiredToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import Usuario


MENSAJE_CREDENCIALES_INVALIDAS = 'Usuario o contraseña incorrectos'
MAXIMOS_FALLOS_LOGIN = 5
VENTANA_FALLOS_LOGIN = 60
logger_seguridad = logging.getLogger('usuarios.seguridad')


def _ip_cliente(request):
    """Obtiene la IP del socket; no confía en X-Forwarded-For no configurado."""
    return request.META.get('REMOTE_ADDR') or 'desconocida'


def _valor_log(valor, limite=300):
    """Evita saltos de línea y tamaños arbitrarios en los registros de seguridad."""
    return str(valor).replace('\r', '\\r').replace('\n', '\\n')[:limite]


def _username_parcial(username):
    """Anonimiza el username sin escribir la credencial completa en el log."""
    valor = str(username or '')
    if not valor:
        return 'anonimo'
    return hashlib.sha256(valor.encode('utf-8')).hexdigest()[:12]


def _registrar_evento(request, resultado, username=''):
    logger_seguridad.info(
        'fecha=%s resultado=%s username=%s ip=%s user_agent=%s',
        timezone.now().isoformat(),
        resultado,
        _username_parcial(username),
        _valor_log(_ip_cliente(request)),
        _valor_log(request.META.get('HTTP_USER_AGENT', 'desconocido')),
    )


def _clave_throttling(ip):
    return 'login-fallos:' + hashlib.sha256(ip.encode('utf-8')).hexdigest()


def _fallos_vigentes(ip, ahora=None):
    ahora = ahora or timezone.now()
    limite = ahora.timestamp() - VENTANA_FALLOS_LOGIN
    return [marca for marca in cache.get(_clave_throttling(ip), []) if marca > limite]


def _login_bloqueado(ip):
    return len(_fallos_vigentes(ip)) >= MAXIMOS_FALLOS_LOGIN


def _registrar_fallo_login(ip):
    ahora = timezone.now()
    fallos = _fallos_vigentes(ip, ahora)
    fallos.append(ahora.timestamp())
    cache.set(_clave_throttling(ip), fallos, VENTANA_FALLOS_LOGIN)


def _limpiar_fallos_login(ip):
    cache.delete(_clave_throttling(ip))


def _revocar_refresh_vigentes(usuario):
    """Revoca mediante la blacklist estándar todos los refresh aún vigentes."""
    ids_blacklisteados = BlacklistedToken.objects.values_list('token_id', flat=True)
    tokens = OutstandingToken.objects.filter(
        user=usuario,
        expires_at__gt=timezone.now(),
    ).exclude(id__in=ids_blacklisteados)
    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)


def _refresh_blacklisteado(refresh):
    return BlacklistedToken.objects.filter(token__jti=refresh['jti']).exists()


def _establecer_refresh(respuesta, valor):
    """Escribe el refresh solo en la cookie contractual, nunca en el JSON."""
    from django.conf import settings

    respuesta.set_cookie(
        settings.AUTH_COOKIE_NAME,
        valor,
        max_age=60 * 60 * 24,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        path=settings.AUTH_COOKIE_PATH,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
    )


def _borrar_refresh(respuesta):
    from django.conf import settings

    # `delete_cookie` no acepta `secure` en Django; escribir una cookie expirada
    # permite conservar todos los atributos contractuales, incluido Secure.
    respuesta.set_cookie(
        settings.AUTH_COOKIE_NAME,
        '',
        max_age=0,
        expires='Thu, 01 Jan 1970 00:00:00 GMT',
        path=settings.AUTH_COOKIE_PATH,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
    )


class CsrfView(APIView):
    """Entrega una cookie CSRF legible para que el cliente forme el encabezado."""

    permission_classes = [AllowAny]

    def get(self, request):
        get_token(request)
        return Response({'detail': 'CSRF listo'}, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Parsear y validar la forma antes del límite: estos errores no cuentan.
        datos = request.data
        if not isinstance(datos, Mapping) or not datos.get('username') or not datos.get('password'):
            return Response(
                {'detail': 'username y password son obligatorios'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = datos['username']
        ip = _ip_cliente(request)
        if _login_bloqueado(ip):
            _registrar_evento(request, 'throttled', username)
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        usuario = authenticate(
            request,
            username=username,
            password=datos['password'],
        )
        if usuario is None or not usuario.is_active:
            _registrar_fallo_login(ip)
            _registrar_evento(request, 'fallo_credenciales', username)
            return Response(
                {'detail': MENSAJE_CREDENCIALES_INVALIDAS},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if usuario.rol != Usuario.Roles.ADMINISTRATIVO:
            _registrar_evento(request, 'rol_no_autorizado', username)
            return Response(
                {'detail': MENSAJE_CREDENCIALES_INVALIDAS},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        _limpiar_fallos_login(ip)
        refresh = RefreshToken.for_user(usuario)
        respuesta = Response(
            {'access': str(refresh.access_token)},
            status=status.HTTP_200_OK,
        )
        _establecer_refresh(respuesta, str(refresh))
        _registrar_evento(request, 'login_exitoso', username)
        return respuesta


@method_decorator(csrf_protect, name='dispatch')
class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.conf import settings

        valor = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
        if not valor:
            _registrar_evento(request, 'refresh_ausente')
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Se valida firma y expiración antes de usar el payload para revocar.
            refresh = RefreshToken(valor, verify=False)
            refresh.token_backend.decode(valor, verify=True)
            if _refresh_blacklisteado(refresh):
                usuario = Usuario.objects.filter(pk=refresh['user_id']).first()
                if usuario:
                    _revocar_refresh_vigentes(usuario)
                    _registrar_evento(request, 'refresh_reutilizado', usuario.username)
                else:
                    _registrar_evento(request, 'refresh_reutilizado')
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            refresh.verify()
            usuario = Usuario.objects.get(pk=refresh['user_id'])
            if (
                not usuario.is_active
                or usuario.rol != Usuario.Roles.ADMINISTRATIVO
            ):
                raise TokenError('Usuario no autorizado')

            access = str(refresh.access_token)
            refresh.blacklist()
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            refresh.outstand()
            nuevo_refresh = str(refresh)
        except (
            TokenBackendExpiredToken,
            TokenError,
            KeyError,
            TypeError,
            ValueError,
            Usuario.DoesNotExist,
        ):
            _registrar_evento(request, 'refresh_invalido')
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        respuesta = Response({'access': access}, status=status.HTTP_200_OK)
        _establecer_refresh(respuesta, nuevo_refresh)
        _registrar_evento(request, 'refresh_exitoso', usuario.username)
        return respuesta


@method_decorator(csrf_protect, name='dispatch')
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.conf import settings

        valor = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
        if valor:
            try:
                RefreshToken(valor).blacklist()
            except (TokenError, KeyError, TypeError, ValueError):
                pass

        respuesta = Response(status=status.HTTP_204_NO_CONTENT)
        _borrar_refresh(respuesta)
        _registrar_evento(request, 'logout')
        return respuesta
