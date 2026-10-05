from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .acciones import (
    ErrorDeAccion,
    corregir_finalizacion,
    finalizar_componente,
    finalizar_servicio,
    iniciar_trabajo,
    registrar_respuesta,
)
from .models import (
    AprobacionServicio,
    Cliente,
    Componente,
    Cotizacion,
    EstadoCotizacion,
    EstadoServicio,
    Fotografia,
    HistorialServicio,
    MedioAprobacion,
    Servicio,
)
from .serializers import (
    AprobacionCreateSerializer,
    AprobacionServicioSerializer,
    AprobacionWebSerializer,
    ClienteSerializer,
    ComponenteSerializer,
    CorregirFinalizacionInputSerializer,
    CotizacionSerializer,
    FinalizarComponenteInputSerializer,
    FotografiaSerializer,
    HistorialServicioSerializer,
    RespuestaCotizacionInputSerializer,
    ServicioPublicoSerializer,
    ServicioSerializer,
)


def _client_ip(request):
    """Extrae la IP real, considerando proxies (X-Forwarded-For)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ─────────────────────────────────────────────────────────────
# API administrativa (requiere JWT por configuración global)
# ─────────────────────────────────────────────────────────────

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('-fecha_creacion')
    serializer_class = ClienteSerializer
    search_fields = ['nombre', 'empresa', 'telefono', 'email']


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.select_related('cliente').all()
    serializer_class = ServicioSerializer

    def perform_update(self, serializer):
        estado_anterior = self.get_object().estado
        instancia = serializer.save()
        # Trazabilidad: si el estado cambió, se registra en el historial.
        if instancia.estado != estado_anterior:
            HistorialServicio.objects.create(
                servicio=instancia,
                estado=instancia.estado,
                comentario=f'Estado cambiado a {instancia.get_estado_display()}',
                usuario=self.request.user,
                visible_cliente=False,
            )


class CotizacionViewSet(viewsets.ModelViewSet):
    queryset = Cotizacion.objects.select_related('servicio', 'creada_por').all()
    serializer_class = CotizacionSerializer
    search_fields = ['numero', 'servicio__codigo', 'servicio__cliente__nombre']


class ComponenteListCreateView(generics.ListCreateAPIView):
    serializer_class = ComponenteSerializer

    def get_queryset(self):
        return Componente.objects.filter(servicio_id=self.kwargs['servicio_pk'])

    def perform_create(self, serializer):
        serializer.save(
            servicio=get_object_or_404(Servicio, pk=self.kwargs['servicio_pk'])
        )


class HistorialServicioListCreateView(generics.ListCreateAPIView):
    serializer_class = HistorialServicioSerializer

    def get_queryset(self):
        return HistorialServicio.objects.filter(
            servicio_id=self.kwargs['servicio_pk']
        )

    def perform_create(self, serializer):
        serializer.save(
            servicio=get_object_or_404(Servicio, pk=self.kwargs['servicio_pk']),
            usuario=self.request.user,
        )


class FotografiaListCreateView(generics.ListCreateAPIView):
    serializer_class = FotografiaSerializer

    def get_queryset(self):
        return Fotografia.objects.filter(servicio_id=self.kwargs['servicio_pk'])

    def perform_create(self, serializer):
        serializer.save(
            servicio=get_object_or_404(Servicio, pk=self.kwargs['servicio_pk']),
            subida_por=self.request.user,
        )


class AprobacionListCreateView(generics.ListCreateAPIView):
    """Aprobaciones de una cotización registradas por el administrador.

    Aplica para aprobaciones externas (WhatsApp, llamada, presencial, etc.):
    ¿usuario_registro queda como el administrativo que la registró.
    """

    def get_queryset(self):
        return AprobacionServicio.objects.filter(
            cotizacion_id=self.kwargs['cotizacion_pk']
        ).select_related('usuario_registro')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AprobacionCreateSerializer
        return AprobacionServicioSerializer

    def perform_create(self, serializer):
        cotizacion = get_object_or_404(Cotizacion, pk=self.kwargs['cotizacion_pk'])
        aprobacion = serializer.save(
            cotizacion=cotizacion,
            usuario_registro=self.request.user,
            ip=_client_ip(self.request),
            fecha=serializer.validated_data.get('fecha') or timezone.now(),
        )
        # La cotización refleja el resultado de la aprobación.
        cotizacion.estado = aprobacion.resultado
        cotizacion.save(update_fields=['estado'])


# ─────────────────────────────────────────────────────────────
# Acciones de proceso (tarea previa del administrativo)
#
# Estas vistas no deciden nada: validan la entrada, llaman a `acciones.py` y
# traducen el resultado a HTTP. La misma acción la ejecuta el admin (T25 a T27)
# desde el mismo módulo, para que la regla exista en un solo lugar.
# Todas quedan bajo el permiso global IsAuthenticated: registrar una respuesta,
# iniciar trabajo o cerrar un servicio es una decisión interna.
# ─────────────────────────────────────────────────────────────

class _AccionDeComponente(APIView):
    """Base de las acciones sobre un componente de un servicio."""

    def get_servicio(self, servicio_pk):
        return get_object_or_404(Servicio, pk=servicio_pk)


class RespuestaCotizacionView(_AccionDeComponente):
    """Registra la respuesta del cliente a una cotización (RF-COT-03).

    El administrativo hace de intermediario: informa que el cliente respondió
    por web o por WhatsApp. El sistema guarda el canal, quién lo registró y el
    momento (RF-COT-04: canal + responsable + fecha de cada respuesta).

    Si el componente tenía una cotización bloqueante y el cliente la rechaza,
    el componente queda `RECHAZADO_BLOQUEANTE` (RF-COT-05). El estado del
    **servicio** no se toca aquí (RF-COT-13).
    """

    def post(self, request, servicio_pk, componente_pk):
        serializer = RespuestaCotizacionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        try:
            aprobacion = registrar_respuesta(
                servicio=self.get_servicio(servicio_pk),
                componente_id=componente_pk,
                cotizacion_id=datos['cotizacion_id'],
                resultado=datos['resultado'],
                canal=datos['canal'],
                observacion=datos.get('observacion', ''),
                usuario=request.user,
                ip=_client_ip(request),
            )
        except ErrorDeAccion as error:
            return Response(
                {'detail': error.detalle, **error.extra},
                status=error.codigo,
            )

        return Response(
            AprobacionServicioSerializer(aprobacion).data,
            status=status.HTTP_201_CREATED,
        )


class IniciarTrabajoView(_AccionDeComponente):
    """Registra el inicio del trabajo de un componente (RF-COT-08).

    Es donde el backend aplica RF-COT-04: aunque el botón de la interfaz esté
    deshabilitado, la API es la que rechaza el inicio si el componente tiene
    una cotización bloqueante sin resolver.
    """

    def post(self, request, servicio_pk, componente_pk):
        try:
            componente = iniciar_trabajo(
                servicio=self.get_servicio(servicio_pk),
                componente_id=componente_pk,
                usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response(
                {'detail': error.detalle}, status=error.codigo,
            )

        return Response(
            ComponenteSerializer(componente).data, status=status.HTTP_200_OK,
        )


class FinalizarComponenteView(_AccionDeComponente):
    """Finaliza un componente con su motivo (RF-COT-09)."""

    def post(self, request, servicio_pk, componente_pk):
        serializer = FinalizarComponenteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            componente = finalizar_componente(
                servicio=self.get_servicio(servicio_pk),
                componente_id=componente_pk,
                motivo=serializer.validated_data['motivo'],
                usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response(
                {'detail': error.detalle}, status=error.codigo,
            )

        return Response(
            ComponenteSerializer(componente).data, status=status.HTTP_200_OK,
        )


class CorregirFinalizacionView(_AccionDeComponente):
    """Corrige un cierre mal registrado (RF-COT-10)."""

    def post(self, request, servicio_pk, componente_pk):
        serializer = CorregirFinalizacionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        try:
            componente = corregir_finalizacion(
                servicio=self.get_servicio(servicio_pk),
                componente_id=componente_pk,
                nuevo_estado=datos['nuevo_estado'],
                comentario=datos.get('comentario', ''),
                usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response(
                {'detail': error.detalle}, status=error.codigo,
            )

        return Response(
            ComponenteSerializer(componente).data, status=status.HTTP_200_OK,
        )


class FinalizarServicioView(APIView):
    """Cierra el servicio (RF-COT-11).

    El cierre nunca es automático (glosario 4.9): esta es la única vista que
    puede poner un servicio en `FINALIZADO`, y siempre por una llamada
    explícita del administrativo.

    Solo habilita el cierre cuando **todos** los componentes están finalizados
    (criterio único 4.8). El 409 lleva el motivo en `resumen_cierre` para que la
    interfaz pueda explicarlo sin inventar reglas.
    """

    def post(self, request, servicio_pk):
        servicio = get_object_or_404(Servicio, pk=servicio_pk)
        try:
            finalizar_servicio(servicio=servicio, usuario=request.user)
        except ErrorDeAccion as error:
            return Response(
                {'detail': error.detalle, **error.extra},
                status=error.codigo,
            )

        return Response(
            ServicioSerializer(servicio).data, status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────
# API pública (sin login, con token privado)
# ─────────────────────────────────────────────────────────────

class SeguimientoView(generics.RetrieveAPIView):
    """Consulta pública del estado de TU servicio mediante el token privado."""

    permission_classes = [AllowAny]
    serializer_class = ServicioPublicoSerializer
    lookup_field = 'token_seguimiento'
    lookup_url_kwarg = 'token'

    def get_queryset(self):
        return Servicio.objects.filter(activo=True)


class SeguimientoAprobarView(APIView):
    """El cliente aprueba o rechaza la cotización pendiente desde la web.

    Se registra con medio=WEB y sin usuario_registro (acción pública).
    """

    permission_classes = [AllowAny]

    def post(self, request, token):
        servicio = get_object_or_404(
            Servicio, token_seguimiento=token, activo=True
        )
        serializer = AprobacionWebSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cotizacion = (
            servicio.cotizaciones
            .filter(estado=EstadoCotizacion.PENDIENTE)
            .order_by('-fecha_creacion')
            .first()
        )
        if not cotizacion:
            return Response(
                {'detail': 'No hay cotización pendiente de aprobación.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        aprobacion = AprobacionServicio.objects.create(
            cotizacion=cotizacion,
            resultado=serializer.validated_data['resultado'],
            medio=MedioAprobacion.WEB,
            fecha=timezone.now(),
            usuario_registro=None,
            observacion=serializer.validated_data.get('observacion', ''),
            ip=_client_ip(request),
        )
        cotizacion.estado = aprobacion.resultado
        cotizacion.save(update_fields=['estado'])

        return Response(
            AprobacionServicioSerializer(aprobacion).data,
            status=status.HTTP_201_CREATED,
        )
