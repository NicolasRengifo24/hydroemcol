import unicodedata

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Count, Q, F, Value
from django.db.models.functions import Lower, Replace
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .acciones import (
    ErrorDeAccion,
    cambiar_estado_componente,
    finalizar_servicio,
    cancelar_servicio,
    registrar_recepcion,
    registrar_respuesta,
    crear_cotizacion,
    editar_cotizacion,
    reenviar_cotizacion,
    registrar_aprobacion_externa,
    guardar_registro_tecnico,
    crear_fotografia,
    actualizar_fotografia,
    eliminar_fotografia,
    desactivar_servicio,
)
from .almacenamiento import ErrorDeAlmacenamiento, guardar_fotografias
from .mensajes import construir_bloque_whatsapp
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
    TipoServicio,
    RegistroTecnico,
)
from .serializers import (
    AprobacionCreateSerializer,
    AprobacionServicioSerializer,
    AprobacionWebSerializer,
    CambiarEstadoComponenteInputSerializer,
    CancelarServicioInputSerializer,
    FinalizarServicioInputSerializer,
    RegistrarRecepcionInputSerializer,
    ClienteSerializer,
    ComponenteAdministrativoSerializer,
    ComponenteSerializer,
    CotizacionSerializer,
    FotografiaSerializer,
    HistorialServicioSerializer,
    RespuestaCotizacionInputSerializer,
    ServicioPublicoSerializer,
    DashboardAdministrativoSerializer,
    ServicioAdministrativoSerializer,
    ServicioResumenAdministrativoSerializer,
    ServicioSerializer,
    SolicitudPublicaSerializer,
    ReenviarCotizacionSerializer,
    RegistroTecnicoSerializer,
    RegistroTecnicoInputSerializer,
    FotografiaAdministrativaSerializer,
    FOTOGRAFIA_FORMATOS,
    FOTOGRAFIA_TAMANO_MAX,
)
from .validators import validar_celular_colombiano


def _client_ip(request):
    """Extrae la IP real, considerando proxies (X-Forwarded-For)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class EsAdministrativo(BasePermission):
    """Autorización de backend para todas las rutas administrativas."""

    message = 'Se requiere una cuenta administrativa activa.'

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.is_active
            and getattr(usuario, 'rol', None) == 'ADMINISTRATIVO'
        )


# ─────────────────────────────────────────────────────────────
# API administrativa (requiere JWT por configuración global)
# ─────────────────────────────────────────────────────────────

class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [EsAdministrativo]
    queryset = Cliente.objects.all().order_by('-fecha_creacion')
    serializer_class = ClienteSerializer
    search_fields = ['nombre', 'empresa', 'telefono', 'email']


class ServicioViewSet(viewsets.ModelViewSet):
    permission_classes = [EsAdministrativo]
    queryset = Servicio.objects.select_related('cliente').all()
    serializer_class = ServicioSerializer

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve', 'update', 'partial_update'}:
            return ServicioAdministrativoSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = self.queryset
        if self.action == 'list':
            # Los cancelados aparecen en el listado administrativo; el filtro
            # de estado permite aislarlos.
            queryset = queryset.filter(activo=True)
            queryset = _filtrar_servicios(queryset, self.request)
        if self.action == 'retrieve':
            queryset = _optimizar_detalle(queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        ordering = _ordenamiento(request)
        queryset = queryset.order_by(ordering)
        paginator = Paginator(queryset, 10)
        try:
            pagina = paginator.page(request.query_params.get('page', 1))
        except (PageNotAnInteger, EmptyPage):
            return Response({'detail': 'La página solicitada no existe.'}, status=404)

        def enlace(numero):
            if not numero:
                return None
            parametros = request.query_params.copy()
            parametros['page'] = numero
            return request.build_absolute_uri(f'?{parametros.urlencode()}')

        return Response({
            'count': paginator.count,
            'next': enlace(pagina.next_page_number() if pagina.has_next() else None),
            'previous': enlace(pagina.previous_page_number() if pagina.has_previous() else None),
            'page': pagina.number,
            'page_size': 10,
            'results': ServicioResumenAdministrativoSerializer(pagina.object_list, many=True).data,
        })

    def perform_update(self, serializer):
        with transaction.atomic():
            instancia = Servicio.objects.select_for_update().get(pk=self.get_object().pk)
            serializer.instance = instancia
            instancia = serializer.save()
            HistorialServicio.objects.create(
                servicio=instancia, estado=instancia.estado,
                comentario='Observaciones internas actualizadas.',
                usuario=self.request.user, visible_cliente=False,
            )

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Los servicios se crean mediante la solicitud pública.'}, status=405)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Los servicios se desactivan; no se eliminan.'}, status=405)


class CotizacionViewSet(viewsets.ModelViewSet):
    permission_classes = [EsAdministrativo]
    queryset = Cotizacion.objects.select_related('servicio', 'creada_por').all()
    serializer_class = CotizacionSerializer
    search_fields = ['numero', 'servicio__codigo', 'servicio__cliente__nombre']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cotizacion = crear_cotizacion(datos=dict(serializer.validated_data), usuario=request.user)
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        return Response(self.get_serializer(cotizacion).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        parcial = kwargs.pop('partial', False)
        instancia = self.get_object()
        if any(campo in request.data for campo in ('estado', 'canal', 'total')):
            return Response(
                {'detail': 'El estado, canal y total los determina el backend.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instancia, data=request.data, partial=parcial)
        serializer.is_valid(raise_exception=True)
        try:
            cotizacion = editar_cotizacion(
                cotizacion_id=instancia.pk,
                datos=dict(serializer.validated_data), usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        return Response(self.get_serializer(cotizacion).data)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Las cotizaciones forman parte de la trazabilidad y no se eliminan.'}, status=409)

    @action(detail=True, methods=['post'], url_path='reenviar')
    def reenviar(self, request, pk=None):
        serializer = ReenviarCotizacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            nueva = reenviar_cotizacion(
                cotizacion_id=pk, datos=dict(serializer.validated_data), usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        except Cotizacion.DoesNotExist:
            return Response({'detail': 'Cotización no encontrada.'}, status=404)
        return Response(self.get_serializer(nueva).data, status=status.HTTP_201_CREATED)


class ComponenteListCreateView(generics.ListCreateAPIView):
    permission_classes = [EsAdministrativo]
    serializer_class = ComponenteSerializer

    def get_queryset(self):
        return Componente.objects.filter(servicio_id=self.kwargs['servicio_pk'])

    def perform_create(self, serializer):
        serializer.save(
            servicio=get_object_or_404(Servicio, pk=self.kwargs['servicio_pk'])
        )


class ComponenteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [EsAdministrativo]
    serializer_class = ComponenteSerializer

    def get_queryset(self):
        return Componente.objects.filter(servicio_id=self.kwargs['servicio_pk'])

    def perform_update(self, serializer):
        with transaction.atomic():
            servicio = Servicio.objects.select_for_update().get(pk=self.kwargs['servicio_pk'])
            componente = Componente.objects.select_for_update().get(
                pk=self.kwargs['pk'], servicio_id=servicio.pk,
            )
            serializer.instance = componente
            serializer.save()
            HistorialServicio.objects.create(
                servicio=servicio, estado=servicio.estado,
                comentario='Datos descriptivos del componente actualizados.',
                usuario=self.request.user, visible_cliente=False,
            )

    def update(self, request, *args, **kwargs):
        if any(campo in request.data for campo in ('estado', 'fase', 'trabajo_iniciado')):
            return Response(
                {'detail': 'El estado del componente solo cambia mediante una acción de proceso.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)
    def perform_destroy(self, instance):
        with transaction.atomic():
            servicio = Servicio.objects.select_for_update().get(pk=instance.servicio_id)
            componente = Componente.objects.select_for_update().get(pk=instance.pk)
            if componente.historial.exists() or componente.cotizaciones.exists():
                from rest_framework.exceptions import ValidationError
                raise ValidationError('El componente conserva trazabilidad y no puede eliminarse.')
            componente.delete()
            _historial_accion = HistorialServicio.objects.create
            _historial_accion(
                servicio=servicio, estado=servicio.estado,
                comentario='Componente sin trazabilidad eliminado.',
                usuario=self.request.user, visible_cliente=False,
            )


class HistorialServicioListCreateView(generics.ListCreateAPIView):
    permission_classes = [EsAdministrativo]
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
    permission_classes = [EsAdministrativo]
    serializer_class = FotografiaSerializer

    def get_queryset(self):
        return Fotografia.objects.filter(servicio_id=self.kwargs['servicio_pk'])

    def perform_create(self, serializer):
        servicio = get_object_or_404(Servicio, pk=self.kwargs['servicio_pk'])
        datos = dict(serializer.validated_data)
        archivo = self.request.FILES.get('archivo')
        if archivo is None and not datos.get('url'):
            raise ErrorDeAccion('Indica un archivo o una referencia de almacenamiento.', 400)
        if archivo is not None:
            extension = archivo.name.rsplit('.', 1)[-1].lower() if '.' in archivo.name else ''
            if extension not in FOTOGRAFIA_FORMATOS:
                raise ErrorDeAccion('Formato no admitido: solo se aceptan JPG, JPEG o PNG.', 400)
            if archivo.size > FOTOGRAFIA_TAMANO_MAX:
                raise ErrorDeAccion('La fotografía supera el límite de 10 MB por archivo.', 400)
        try:
            self._fotografia_creada = crear_fotografia(
                servicio_id=servicio.pk, datos=datos, archivo=archivo, usuario=self.request.user,
            )
        except ErrorDeAccion:
            raise

    def get_serializer_class(self):
        return FotografiaAdministrativaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if 'archivo' in request.FILES:
            datos = request.data.copy()
            datos['url'] = ''
            serializer = self.get_serializer(data=datos)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        return Response(self.get_serializer(self._fotografia_creada).data, status=201)


class FotografiaDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [EsAdministrativo]
    serializer_class = FotografiaAdministrativaSerializer

    def get_queryset(self):
        return Fotografia.objects.filter(servicio_id=self.kwargs['servicio_pk'])

    def update(self, request, *args, **kwargs):
        fotografia = self.get_object()
        serializer = self.get_serializer(fotografia, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        try:
            fotografia = actualizar_fotografia(
                servicio_id=self.kwargs['servicio_pk'], fotografia_id=fotografia.pk,
                datos=dict(serializer.validated_data), usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        return Response(self.get_serializer(fotografia).data)

    def destroy(self, request, *args, **kwargs):
        fotografia = self.get_object()
        try:
            eliminar_fotografia(
                servicio_id=self.kwargs['servicio_pk'], fotografia_id=fotografia.pk,
                usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        return Response(status=204)


class RegistroTecnicoView(APIView):
    permission_classes = [EsAdministrativo]

    def get(self, request, servicio_pk):
        servicio = get_object_or_404(Servicio, pk=servicio_pk)
        registro = RegistroTecnico.objects.filter(servicio=servicio).first()
        return Response(RegistroTecnicoSerializer(registro).data if registro else None)

    def post(self, request, servicio_pk):
        serializer = RegistroTecnicoInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if RegistroTecnico.objects.filter(servicio_id=servicio_pk).exists():
            return Response({'detail': 'El registro técnico ya existe; usa PATCH.'}, status=409)
        try:
            registro = guardar_registro_tecnico(servicio_id=servicio_pk, datos=dict(serializer.validated_data), usuario=request.user)
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        return Response(RegistroTecnicoSerializer(registro).data, status=201)

    def patch(self, request, servicio_pk):
        serializer = RegistroTecnicoInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if not RegistroTecnico.objects.filter(servicio_id=servicio_pk).exists():
            return Response({'detail': 'No existe un registro técnico para actualizar.'}, status=404)
        try:
            registro = guardar_registro_tecnico(servicio_id=servicio_pk, datos=dict(serializer.validated_data), usuario=request.user)
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        return Response(RegistroTecnicoSerializer(registro).data)


class AprobacionListCreateView(generics.ListCreateAPIView):
    permission_classes = [EsAdministrativo]
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
        try:
            aprobacion = registrar_aprobacion_externa(
                cotizacion_id=cotizacion.pk,
                resultado=serializer.validated_data['resultado'],
                medio=serializer.validated_data['medio'],
                usuario=self.request.user,
                ip=_client_ip(self.request),
                fecha=serializer.validated_data.get('fecha') or timezone.now(),
                observacion=serializer.validated_data.get('observacion', ''),
            )
        except ErrorDeAccion:
            raise
        self._aprobacion_creada = aprobacion

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        return Response(AprobacionServicioSerializer(self._aprobacion_creada).data, status=201)


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

    permission_classes = [EsAdministrativo]

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


class CambiarEstadoComponenteView(_AccionDeComponente):
    """Cambia el estado operativo de un componente (RF-EST-03..08).

    La vista no decide: valida la entrada, delega en `acciones.py` y traduce
    el resultado a HTTP, igual que las demás acciones administrativas. Los
    estados derivados (APROBADO, RECHAZADO, RECHAZADO_BLOQUEANTE) los rechaza
    la acción con 400 (CL-03), y el bloqueo por cotización con 409.
    """

    def post(self, request, servicio_pk, componente_pk):
        serializer = CambiarEstadoComponenteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        try:
            componente = cambiar_estado_componente(
                servicio=self.get_servicio(servicio_pk),
                componente_id=componente_pk,
                nuevo_estado=datos['estado'],
                comentario=datos.get('comentario', ''),
                usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response(
                {'detail': error.detalle}, status=error.codigo,
            )

        return Response(
            ComponenteAdministrativoSerializer(componente).data,
            status=status.HTTP_200_OK,
        )


class ServicioWhatsAppView(APIView):
    """Prepara, bajo demanda, las tarjetas de WhatsApp de un servicio."""

    permission_classes = [EsAdministrativo]

    def get(self, request, servicio_pk):
        servicio = get_object_or_404(
            Servicio.objects.select_related('cliente'), pk=servicio_pk,
        )
        componentes = servicio.componentes.all()
        datos_servicio = {
            'codigo': servicio.codigo,
            'estado': servicio.estado,
            'activo': servicio.activo,
            'token_seguimiento': servicio.token_seguimiento,
        }
        datos_componentes = [
            {
                'id': componente.pk,
                'tipo': componente.tipo,
                'referencia': componente.referencia,
                'estado': componente.estado,
                'motivo_finalizacion': componente.motivo_finalizacion,
            }
            for componente in componentes
        ]
        numero = validar_celular_colombiano(servicio.cliente.whatsapp)
        bloque = construir_bloque_whatsapp(
            datos_servicio,
            datos_componentes,
            settings.SEGUIMIENTO_BASE_URL,
            numero,
        )
        return Response(bloque)


class FinalizarServicioView(APIView):
    """Cierra el servicio (RF-COT-11).

    El cierre nunca es automático (glosario 4.9): esta es la única vista que
    puede poner un servicio en `FINALIZADO`, y siempre por una llamada
    explícita del administrativo.

    Solo habilita el cierre cuando **todos** los componentes están finalizados
    (criterio único 4.8). El 409 lleva el motivo en `resumen_cierre` para que la
    interfaz pueda explicarlo sin inventar reglas.
    """

    permission_classes = [EsAdministrativo]

    def post(self, request, servicio_pk):
        servicio = get_object_or_404(Servicio, pk=servicio_pk)
        serializer = FinalizarServicioInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            servicio = finalizar_servicio(
                servicio=servicio, comentario=serializer.validated_data.get('comentario', ''),
                usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response(
                {'detail': error.detalle, **error.extra},
                status=error.codigo,
            )

        return Response(
            ServicioAdministrativoSerializer(servicio).data, status=status.HTTP_200_OK,
        )


class RegistrarRecepcionView(APIView):
    """Registra que los componentes del servicio llegaron al almacén.

    La recepción es una acción explícita del administrativo, no automática. Se
    registra una sola vez y, si el servicio seguía en `SOLICITADO`, lo pasa a
    `EN_CURSO`. El comentario es opcional y queda visible al cliente.
    """

    permission_classes = [EsAdministrativo]

    def post(self, request, servicio_pk):
        servicio = get_object_or_404(Servicio, pk=servicio_pk)
        serializer = RegistrarRecepcionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            servicio = registrar_recepcion(
                servicio=servicio,
                comentario=serializer.validated_data.get('comentario', ''),
                usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response(
                {'detail': error.detalle, **error.extra},
                status=error.codigo,
            )

        return Response(
            ServicioAdministrativoSerializer(servicio).data,
            status=status.HTTP_200_OK,
        )


class CancelarServicioView(APIView):
    """Cancela explícitamente un servicio activo (RF-FLU-10)."""
    permission_classes = [EsAdministrativo]

    def post(self, request, servicio_pk):
        servicio = get_object_or_404(Servicio, pk=servicio_pk)
        serializer = CancelarServicioInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            servicio = cancelar_servicio(
                servicio=servicio,
                comentario=serializer.validated_data['comentario'],
                usuario=request.user,
            )
        except ErrorDeAccion as error:
            return Response(
                {'detail': error.detalle, **error.extra},
                status=error.codigo,
            )

        return Response(
            ServicioAdministrativoSerializer(servicio).data,
            status=status.HTTP_200_OK,
        )


class DesactivarServicioView(APIView):
    """Desactiva un servicio conservando toda su información histórica."""

    permission_classes = [EsAdministrativo]

    def post(self, request, servicio_pk):
        try:
            servicio = desactivar_servicio(servicio_id=servicio_pk, usuario=request.user)
        except Servicio.DoesNotExist:
            return Response({'detail': 'Servicio no encontrado.'}, status=404)
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)
        return Response(ServicioAdministrativoSerializer(servicio).data)


def _normalizar_busqueda(valor):
    texto = unicodedata.normalize('NFD', str(valor or ''))
    return ''.join(caracter for caracter in texto if unicodedata.category(caracter) != 'Mn').lower()


def _expresion_sin_tildes(campo):
    expresion = Lower(F(campo))
    for original, reemplazo in (
        ('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ü', 'u'),
    ):
        expresion = Replace(expresion, Value(original), Value(reemplazo))
    return expresion


def _filtrar_servicios(queryset, request):
    busqueda = _normalizar_busqueda(request.query_params.get('search', ''))
    estado = request.query_params.get('estado')
    estados_validos = {valor for valor, _ in EstadoServicio.choices}
    if estado:
        if estado not in estados_validos:
            return queryset.none()
        queryset = queryset.filter(estado=estado)
    if busqueda:
        queryset = queryset.annotate(
            codigo_normalizado=_expresion_sin_tildes('codigo'),
            nombre_cliente_normalizado=_expresion_sin_tildes('cliente__nombre'),
            empresa_normalizada=_expresion_sin_tildes('cliente__empresa'),
        ).filter(
            Q(codigo_normalizado__contains=busqueda)
            | Q(nombre_cliente_normalizado__contains=busqueda)
            | Q(empresa_normalizada__contains=busqueda)
        )
    return queryset


ORDENAMIENTOS_ADMIN = {
    'fecha_solicitud': 'fecha_solicitud',
    'codigo': 'codigo',
    'estado': 'estado',
    'cliente': 'cliente__nombre',
    'empresa': 'cliente__empresa',
}


def _ordenamiento(request):
    solicitado = request.query_params.get('ordering', '-fecha_solicitud')
    descendente = solicitado.startswith('-')
    nombre = solicitado[1:] if descendente else solicitado
    campo = ORDENAMIENTOS_ADMIN.get(nombre, 'fecha_solicitud')
    return f"{'-' if descendente else ''}{campo}"


def _optimizar_detalle(queryset):
    return queryset.prefetch_related(
        'componentes__historial__usuario',
        'cotizaciones__detalles',
        'cotizaciones__componente',
        'cotizaciones__aprobaciones__usuario_registro',
        'cotizaciones__versiones',
        'historial__usuario',
        'fotografias__subida_por',
        'registro_tecnico__creado_por',
        'registro_tecnico__actualizado_por',
    )


class DashboardAdministrativoView(APIView):
    permission_classes = [EsAdministrativo]

    def get(self, request):
        activos = Servicio.objects.filter(activo=True).select_related('cliente')
        contadores = {
            estado: activos.filter(estado=estado).count()
            for estado, _ in EstadoServicio.choices
        }
        # Trabajo en curso: los cancelados cuentan en los contadores, pero no
        # generan trabajo pendiente ni aparecen en recientes.
        operativos = activos.exclude(estado=EstadoServicio.CANCELADO)
        pendientes = operativos.filter(
            Q(estado__in=[
                EstadoServicio.SOLICITADO,
            ])
            | Q(componentes__estado='ESPERANDO_APROBACION')
        ).distinct().order_by('-fecha_solicitud')
        recientes = operativos.order_by('-fecha_solicitud')[:10]
        datos = {
            'total_activos': activos.count(),
            'contadores': contadores,
            'recientes': recientes,
            'pendientes_atencion': pendientes,
            'definicion': {
                'recientes': 'Últimos 10 servicios no cancelados por fecha_solicitud descendente.',
                'pendientes_atencion': (
                    'Servicios solicitados o con un componente esperando aprobación.'
                ),
            },
        }
        return Response(DashboardAdministrativoSerializer(datos).data)


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
        # Un servicio cancelado sigue activo: el cliente ve que fue cancelado
        # (su enlace no es inválido). Sus cotizaciones pendientes no se listan.
        return Servicio.objects.filter(activo=True)


class SeguimientoAprobarView(APIView):
    """El cliente aprueba o rechaza la cotización pendiente desde la web.

    Se registra con medio=WEB y sin usuario_registro (acción pública).
    """

    permission_classes = [AllowAny]

    def post(self, request, token):
        servicio = get_object_or_404(
            Servicio.objects.exclude(estado=EstadoServicio.CANCELADO),
            token_seguimiento=token, activo=True,
        )
        serializer = AprobacionWebSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cotizacion = servicio.cotizaciones.filter(
            pk=serializer.validated_data['cotizacion_id'],
        ).first()
        if not cotizacion:
            return Response(
                {'detail': 'La cotización no pertenece a este servicio.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            aprobacion = registrar_aprobacion_externa(
                cotizacion_id=cotizacion.pk,
                resultado=serializer.validated_data['resultado'],
                medio=MedioAprobacion.WEB,
                fecha=timezone.now(), usuario=None,
                observacion=serializer.validated_data.get('observacion', ''),
                ip=_client_ip(request),
            )
        except ErrorDeAccion as error:
            return Response({'detail': error.detalle}, status=error.codigo)

        return Response(
            AprobacionServicioSerializer(aprobacion).data,
            status=status.HTTP_201_CREATED,
        )

class SolicitudPublicaCreateView(APIView):
    permission_classes = [AllowAny]

    def _respuesta(self, servicio):
        return {
            'codigo': servicio.codigo,
            'enlace_seguimiento': f'/seguimiento/{servicio.token_seguimiento}',
            'servicio_id': servicio.id,
        }

    def _crear_servicio(self, data, clave):
        """Crea el cliente, el servicio, sus componentes y sus fotografías.

        Todo ocurre en una transacción: si el almacenamiento falla, no queda
        una solicitud a medias ni archivos huérfanos.
        """
        with transaction.atomic():
            cliente, creado = Cliente.objects.get_or_create(
                email=data['correo_electronico'].strip().lower(),
                defaults={
                    'nombre': data['nombre_cliente'].strip(),
                    'empresa': data.get('empresa', '').strip(),
                    'telefono': data.get('telefono', '').strip(),
                    'whatsapp': data.get('whatsapp', '').strip(),
                },
            )
            if not creado and not cliente.whatsapp:
                cliente.whatsapp = data['whatsapp']
                cliente.save(update_fields=['whatsapp'])
            servicio = Servicio.objects.create(
                cliente=cliente,
                tipo_servicio=TipoServicio.PRUEBA,
                descripcion_solicitud=data['descripcion_problema'],
                entregar_en_banco=data.get('entregar_en_banco', False),
                avisar_para_coordinar=data.get('avisar_para_coordinar', False),
                recoger=data.get('recoger', False),
                idempotency_key=clave,
            )
            for comp in data.get('componentes', []):
                Componente.objects.create(
                    servicio=servicio,
                    tipo=comp['tipo'],
                    marca=comp.get('marca') or '',
                    referencia=comp.get('referencia') or '',
                    descripcion=comp.get('descripcion') or '',
                    cantidad=comp.get('cantidad', 1),
                )
            # Las fotografías las guarda un helper separado para poder cambiar
            # el almacenamiento (Cloudflare) sin tocar la vista (plan D-1/D-9).
            guardar_fotografias(servicio, data.get('fotografias'))
            return servicio

    def post(self, request):
        serializer = SolicitudPublicaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        clave = (
            data.get('idempotency_key')
            or request.headers.get('Idempotency-Key')
            or ''
        ).strip()

        if clave:
            existente = Servicio.objects.filter(idempotency_key=clave).first()
            if existente is not None:
                return Response(self._respuesta(existente), status=status.HTTP_200_OK)

        if not data.get('confirmar'):
            from . import reglas

            if reglas.tiene_solicitud_en_curso(
                None,
                correo_norm=data.get('correo_electronico'),
                telefono_norm=data.get('telefono'),
                whatsapp_norm=data.get('whatsapp'),
            ):
                return Response(
                    {
                        'requiere_confirmacion': True,
                        'detail': (
                            'Parece que ya tienes una solicitud en curso. '
                            '¿Quieres continuar o crear una nueva?'
                        ),
                    },
                    status=status.HTTP_409_CONFLICT,
                )

        try:
            servicio = self._crear_servicio(data, clave)
        except ErrorDeAlmacenamiento:
            return Response(
                {
                    'detail': (
                        'No pudimos guardar las fotografías de tu solicitud. '
                        'Inténtalo de nuevo en unos minutos o escríbenos por '
                        'WhatsApp para enviar las imágenes.'
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(self._respuesta(servicio), status=status.HTTP_201_CREATED)
