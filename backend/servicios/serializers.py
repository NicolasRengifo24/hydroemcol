from pathlib import Path

from rest_framework import serializers

from .estados import (
    CanalRespuesta,
    ESTADOS_FINALIZACION,
    EstadoComponente,
)
from .models import (
    AprobacionServicio,
    Cliente,
    Componente,
    Cotizacion,
    DetalleCotizacion,
    EstadoCotizacion,
    EstadoServicio,
    Fotografia,
    HistorialComponente,
    HistorialServicio,
    MedioAprobacion,
    RegistroTecnico,
    ResultadoAprobacion,
    Servicio,
)
from .reglas import (
    estados_componente_seleccionables,
    puede_cancelar_servicio,
    resumen_cierre,
    tiene_trabajo_iniciado,
)


def construir_hoy(servicio):
    """Arma el estado que consumen las funciones puras de `reglas.py`.

    Es el único punto del proyecto que traduce modelos a las llaves que
    esperan las reglas. Las reglas siguen sin tocar la base de datos; aquí solo
    se leen los datos del servicio ya cargados.
    """
    componentes = list(servicio.componentes.all())

    cotizaciones_por_componente = {}
    for cotizacion in servicio.cotizaciones.all():
        if cotizacion.componente_id is None:
            continue
        cotizaciones_por_componente.setdefault(cotizacion.componente_id, []).append({
            'id': cotizacion.pk,
            'es_bloqueante': cotizacion.es_bloqueante,
            'estado': cotizacion.estado,
        })

    return {
        'componentes': [
            {
                'id': componente.pk,
                'estado': componente.estado,
                'trabajo_iniciado': componente.trabajo_iniciado,
            }
            for componente in componentes
        ],
        'cotizaciones_por_componente': cotizaciones_por_componente,
        'cotizaciones': [
            cotizacion
            for lista in cotizaciones_por_componente.values()
            for cotizacion in lista
        ],
        # Llaves de servicio que consumen las reglas de estado de la spec 006.
        'estado': servicio.estado,
        'activo': servicio.activo,
    }


# ─────────────────────────────────────────────────────────────
# Serializers administrativos
# Los campos de elección trabajan con el valor crudo (ej. "DIAGNOSTICO",
# "SOLICITADO"); el frontend es quien muestra la etiqueta en español.
# ─────────────────────────────────────────────────────────────

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id', 'nombre', 'empresa', 'telefono', 'whatsapp', 'email',
            'direccion', 'ciudad', 'fecha_creacion',
        ]
        read_only_fields = ['fecha_creacion']


class ComponenteSerializer(serializers.ModelSerializer):
    motivo_espera = serializers.SerializerMethodField()

    class Meta:
        model = Componente
        fields = [
            'id', 'servicio', 'tipo', 'marca', 'referencia', 'descripcion',
            'cantidad', 'estado', 'fase', 'trabajo_iniciado',
            'fecha_inicio_trabajo', 'fecha_finalizacion', 'motivo_finalizacion',
            'motivo_espera',
        ]
        read_only_fields = [
            'servicio',
            # El estado del componente lo decide el backend. Permitirlo escribir
            # desde el cliente dejaría la puerta abierta a cerrar un componente
            # sin pasar por la validación (constitución principio 3).
            'estado',
            'fase',
            'trabajo_iniciado',
            'fecha_inicio_trabajo',
            'fecha_finalizacion',
            'motivo_finalizacion',
        ]

    def _reglas_del_servicio(self, obj):
        return construir_hoy(obj.servicio)

    def get_motivo_espera(self, obj):
        if obj.estado != EstadoComponente.ESPERANDO_APROBACION:
            return None
        pendiente = obj.servicio.cotizaciones.filter(
            componente=obj, estado=EstadoCotizacion.PENDIENTE,
        ).exists()
        return (
            'Cotización pendiente de respuesta' if pendiente else
            'Cotización rechazada: reenviar o finalizar como RECHAZADO'
        )


class DetalleCotizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCotizacion
        fields = ['id', 'descripcion', 'valor', 'cantidad']


class HistorialServicioSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(read_only=True)
    usuario = serializers.SerializerMethodField()

    class Meta:
        model = HistorialServicio
        fields = ['id', 'servicio', 'estado', 'comentario', 'fecha', 'usuario', 'visible_cliente']
        read_only_fields = ['servicio']

    def get_usuario(self, obj):
        return obj.usuario.username if obj.usuario else None


class FotografiaSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(read_only=True)
    subida_por = serializers.SerializerMethodField()

    class Meta:
        model = Fotografia
        fields = ['id', 'servicio', 'url', 'descripcion', 'tipo', 'visible_cliente', 'fecha', 'subida_por']
        read_only_fields = ['servicio']

    def get_subida_por(self, obj):
        return obj.subida_por.username if obj.subida_por else None


class AprobacionServicioSerializer(serializers.ModelSerializer):
    usuario_registro = serializers.SerializerMethodField()
    fecha_registro = serializers.DateTimeField(read_only=True)

    class Meta:
        model = AprobacionServicio
        fields = [
            'id', 'cotizacion', 'resultado', 'medio', 'fecha',
            'usuario_registro', 'observacion', 'ip', 'fecha_registro',
        ]

    def get_usuario_registro(self, obj):
        return obj.usuario_registro.username if obj.usuario_registro else None


class AprobacionCreateSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(required=False)

    class Meta:
        model = AprobacionServicio
        fields = ['id', 'resultado', 'medio', 'fecha', 'observacion']


class AprobacionWebSerializer(serializers.Serializer):
    """Aprobación que realiza el cliente en la web.

    No pide 'medio': el sistema sabe que la aprobación es por la web (WEB).
    """

    resultado = serializers.ChoiceField(choices=ResultadoAprobacion.choices)
    observacion = serializers.CharField(required=False, allow_blank=True)


class CotizacionSerializer(serializers.ModelSerializer):
    detalles = DetalleCotizacionSerializer(many=True)
    numero = serializers.CharField(read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
    total = serializers.SerializerMethodField()
    creada_por = serializers.SerializerMethodField()

    class Meta:
        model = Cotizacion
        fields = [
            'id', 'servicio', 'numero', 'tipo', 'descripcion', 'total',
            'estado', 'fecha_creacion', 'observaciones', 'creada_por', 'detalles',
            'componente', 'es_bloqueante', 'canal',
        ]
        read_only_fields = [
            # `canal` solo se escribe al registrar la respuesta; la clasificación
            # `es_bloqueante` sí se define al presentar la cotización.
            'canal',
            'estado',
            'total',
        ]

    def validate(self, attrs):
        if self.instance is not None:
            attrs.pop('es_bloqueante', None)
        servicio = attrs.get('servicio') or getattr(self.instance, 'servicio', None)
        componente = attrs.get('componente')
        if componente is not None and servicio is not None and componente.servicio_id != servicio.pk:
            raise serializers.ValidationError('El componente no pertenece al servicio indicado.')
        return attrs

    def get_total(self, obj):
        return str(obj.total)

    def get_creada_por(self, obj):
        return obj.creada_por.username if obj.creada_por else None

    @staticmethod
    def _calcular_total(detalles_data):
        return sum(
            detalle['valor'] * detalle['cantidad']
            for detalle in detalles_data
        )

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        validated_data['creada_por'] = self.context['request'].user
        cotizacion = Cotizacion.objects.create(**validated_data)
        for detalle in detalles_data:
            DetalleCotizacion.objects.create(cotizacion=cotizacion, **detalle)
        cotizacion.total = self._calcular_total(detalles_data)
        cotizacion.save(update_fields=['total'])
        return cotizacion

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if detalles_data is not None:
            instance.detalles.all().delete()
            for detalle in detalles_data:
                DetalleCotizacion.objects.create(cotizacion=instance, **detalle)
            instance.total = self._calcular_total(detalles_data)
        instance.save()
        return instance


class ReenviarCotizacionSerializer(serializers.Serializer):
    descripcion = serializers.CharField(required=False, allow_blank=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    detalles = DetalleCotizacionSerializer(many=True, required=False, default=list)


class ServicioSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        source='cliente', queryset=Cliente.objects.all(),
        write_only=True,
    )
    codigo = serializers.CharField(read_only=True)
    token_seguimiento = serializers.CharField(read_only=True)
    fecha_solicitud = serializers.DateTimeField(read_only=True)
    resumen_cierre = serializers.SerializerMethodField()

    class Meta:
        model = Servicio
        fields = [
            'id', 'codigo', 'cliente', 'cliente_id', 'tipo_servicio', 'estado',
            'descripcion_solicitud', 'entregar_en_banco', 'avisar_para_coordinar',
            'recoger', 'fecha_solicitud', 'fecha_recepcion',
            'fecha_finalizacion', 'fecha_entrega', 'token_seguimiento',
            'observaciones_internas', 'activo', 'resumen_cierre',
        ]
        read_only_fields = ['resumen_cierre']

    def get_resumen_cierre(self, obj):
        """Dice si el cierre está habilitado y por qué, sin ejecutarlo.

        Finalizar el servicio es una acción manual del administrativo y pasa
        por su propia vista (RF-COT-11). Este campo solo informa.
        """
        return resumen_cierre(construir_hoy(obj))


class RegistroTecnicoSerializer(serializers.ModelSerializer):
    creado_por = serializers.SerializerMethodField()
    actualizado_por = serializers.SerializerMethodField()

    class Meta:
        model = RegistroTecnico
        fields = [
            'id', 'diagnostico', 'trabajo_realizado', 'resultado_pruebas',
            'recomendaciones', 'observaciones', 'creado_por', 'actualizado_por',
            'fecha_creacion', 'fecha_actualizacion',
        ]
        read_only_fields = [
            'id', 'creado_por', 'actualizado_por', 'fecha_creacion', 'fecha_actualizacion',
        ]

    def get_creado_por(self, obj):
        return obj.creado_por.username if obj.creado_por else None

    def get_actualizado_por(self, obj):
        return obj.actualizado_por.username if obj.actualizado_por else None


class RegistroTecnicoInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroTecnico
        fields = ['diagnostico', 'trabajo_realizado', 'resultado_pruebas', 'recomendaciones', 'observaciones']


class FotografiaAdministrativaSerializer(serializers.ModelSerializer):
    url = serializers.URLField(required=False, allow_blank=True)
    fecha = serializers.DateTimeField(read_only=True)
    subida_por = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Fotografia
        fields = ['id', 'servicio', 'url', 'descripcion', 'tipo', 'visible_cliente', 'fecha', 'subida_por']
        read_only_fields = ['id', 'servicio', 'fecha', 'subida_por']

    def get_subida_por(self, obj):
        return obj.subida_por.username if obj.subida_por else None


class AprobacionAdministrativaSerializer(AprobacionServicioSerializer):
    """Representación de lectura estable para una cotización administrativa."""

    class Meta(AprobacionServicioSerializer.Meta):
        fields = AprobacionServicioSerializer.Meta.fields


class CotizacionAdministrativaSerializer(serializers.ModelSerializer):
    detalles = DetalleCotizacionSerializer(many=True, read_only=True)
    aprobaciones = AprobacionAdministrativaSerializer(many=True, read_only=True)
    creada_por = serializers.SerializerMethodField()
    reemplaza_a = serializers.IntegerField(source='reemplaza_a_id', read_only=True)
    versiones = serializers.SerializerMethodField()
    etiqueta_componente = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cotizacion
        fields = [
            'id', 'numero', 'tipo', 'descripcion', 'total', 'estado',
            'fecha_creacion', 'observaciones', 'creada_por', 'componente',
            'etiqueta_componente', 'es_bloqueante', 'canal', 'detalles',
            'aprobaciones', 'reemplaza_a', 'versiones',
        ]

    def get_creada_por(self, obj):
        return obj.creada_por.username if obj.creada_por else None

    def get_versiones(self, obj):
        return [version.id for version in obj.versiones.all()]

    def get_etiqueta_componente(self, obj):
        return str(obj.componente) if obj.componente_id else 'Cotización del servicio'

    def get_total(self, obj):
        return str(obj.total)


class HistorialComponenteAdministrativoSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()

    class Meta:
        model = HistorialComponente
        fields = [
            'id', 'estado_anterior', 'estado_nuevo', 'fase_registrada',
            'comentario', 'fecha', 'usuario',
        ]

    def get_usuario(self, obj):
        return obj.usuario.username if obj.usuario else None


class ComponenteAdministrativoSerializer(ComponenteSerializer):
    historial = HistorialComponenteAdministrativoSerializer(many=True, read_only=True)
    acciones_disponibles = serializers.SerializerMethodField()
    estados_seleccionables = serializers.SerializerMethodField()
    etiqueta_estado = serializers.CharField(source='get_estado_display', read_only=True)
    etiqueta_fase = serializers.CharField(source='get_fase_display', read_only=True)

    class Meta(ComponenteSerializer.Meta):
        fields = ComponenteSerializer.Meta.fields + [
            'etiqueta_estado', 'etiqueta_fase', 'historial',
            'acciones_disponibles', 'estados_seleccionables',
        ]

    def get_acciones_disponibles(self, obj):
        if obj.servicio.estado in (EstadoServicio.FINALIZADO, EstadoServicio.CANCELADO):
            return []
        hoy = construir_hoy(obj.servicio)
        componente = next(c for c in hoy['componentes'] if c['id'] == obj.pk)
        acciones = []
        if obj.estado in ESTADOS_FINALIZACION:
            acciones.append('corregir_finalizacion')
        if any(
            cotizacion.componente_id == obj.pk
            and cotizacion.estado == EstadoCotizacion.PENDIENTE
            for cotizacion in obj.servicio.cotizaciones.all()
        ):
            acciones.append('responder_cotizacion')
        return acciones

    def get_estados_seleccionables(self, obj):
        """Opciones de estado que el backend autoriza para este componente.

        Las calcula `reglas.py`: excluyen los estados derivados y, en
        `RECHAZADO_BLOQUEANTE`, solo ofrecen finalizar (RF-EST-01).
        """
        hoy = construir_hoy(obj.servicio)
        componente = next(c for c in hoy['componentes'] if c['id'] == obj.pk)
        return list(estados_componente_seleccionables(hoy, componente))


class ServicioResumenAdministrativoSerializer(serializers.ModelSerializer):
    cliente = serializers.SerializerMethodField()
    tipo_servicio = serializers.CharField(source='get_tipo_servicio_display', read_only=True)
    estado = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Servicio
        fields = ['id', 'codigo', 'cliente', 'tipo_servicio', 'estado', 'fecha_solicitud']

    def get_cliente(self, obj):
        return {'nombre': obj.cliente.nombre, 'empresa': obj.cliente.empresa}


class ServicioAdministrativoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    tipo_servicio = serializers.CharField(source='get_tipo_servicio_display', read_only=True)
    estado = serializers.CharField(source='get_estado_display', read_only=True)
    componentes = ComponenteAdministrativoSerializer(many=True, read_only=True)
    cotizaciones = CotizacionAdministrativaSerializer(many=True, read_only=True)
    historial = HistorialServicioSerializer(many=True, read_only=True)
    fotografias = FotografiaSerializer(many=True, read_only=True)
    registro_tecnico = RegistroTecnicoSerializer(read_only=True, allow_null=True)
    resumen_cierre = serializers.SerializerMethodField()
    acciones_disponibles = serializers.SerializerMethodField()
    seguimiento = serializers.SerializerMethodField()

    class Meta:
        model = Servicio
        fields = [
            'id', 'codigo', 'cliente', 'tipo_servicio', 'estado',
            'descripcion_solicitud', 'entregar_en_banco', 'avisar_para_coordinar',
            'recoger', 'fecha_solicitud', 'fecha_recepcion', 'fecha_finalizacion',
            'fecha_entrega', 'observaciones_internas', 'activo', 'componentes',
            'cotizaciones', 'historial', 'fotografias', 'registro_tecnico',
            'resumen_cierre', 'acciones_disponibles',
            'seguimiento',
        ]
        read_only_fields = [field for field in fields if field != 'observaciones_internas']

    def get_resumen_cierre(self, obj):
        return resumen_cierre(construir_hoy(obj))

    def validate(self, attrs):
        campos_no_permitidos = set(self.initial_data) - {'observaciones_internas'}
        if campos_no_permitidos and self.instance is not None:
            raise serializers.ValidationError(
                'Solo se pueden actualizar las observaciones internas.'
            )
        return attrs

    def get_acciones_disponibles(self, obj):
        if obj.estado in (EstadoServicio.FINALIZADO, EstadoServicio.CANCELADO):
            return []
        hoy = construir_hoy(obj)
        acciones = []
        if resumen_cierre(hoy)['puede_finalizar']:
            acciones.append('finalizar_servicio')
        if puede_cancelar_servicio(hoy):
            acciones.append('cancelar_servicio')
        return acciones

    def get_seguimiento(self, obj):
        # El token es una credencial: solo se entrega como destino de una acción,
        # nunca como un campo independiente o texto descriptivo.
        return {
            'disponible': bool(obj.activo),
            'acciones': ['copiar', 'abrir'] if obj.activo else [],
            'enlace': f'/seguimiento/{obj.token_seguimiento}' if obj.activo else None,
        }


class DashboardAdministrativoSerializer(serializers.Serializer):
    total_activos = serializers.IntegerField()
    contadores = serializers.DictField()
    recientes = ServicioResumenAdministrativoSerializer(many=True)
    pendientes_atencion = ServicioResumenAdministrativoSerializer(many=True)
    definicion = serializers.DictField()


# ─────────────────────────────────────────────────────────────
# Serializers de entrada de las acciones de proceso
# Validan lo que la acción necesita; el efecto sobre el modelo lo
# aplica la vista, que es quien puede usar `reglas.py`.
# ─────────────────────────────────────────────────────────────

class RespuestaCotizacionInputSerializer(serializers.Serializer):
    """Respuesta del cliente a la cotización de un componente (RF-COT-03).

    Exige `canal` porque la definición de RF-COT-03 dice "en el momento en que
    el cliente responde", no "en algún momento posterior": la respuesta es web
    o WhatsApp porque así se enteró, no porque el administrativo lo etiquete
    después. Por eso `canal` es obligatorio aquí y de solo lectura en el
    serializer de la cotización.
    """

    cotizacion_id = serializers.IntegerField()
    resultado = serializers.ChoiceField(choices=ResultadoAprobacion.choices)
    canal = serializers.ChoiceField(choices=CanalRespuesta.choices)
    observacion = serializers.CharField(required=False, allow_blank=True, default='')


class CambiarEstadoComponenteInputSerializer(serializers.Serializer):
    """Entrada del cambio de estado operativo de un componente (RF-EST-03).

    Solo acepta el catálogo de estados: la acción revalida además las reglas
    vigentes, así que el serializer no decide transiciones (principio 3).
    """

    estado = serializers.ChoiceField(choices=EstadoComponente.choices)
    comentario = serializers.CharField(required=False, allow_blank=True, default='')


class CancelarServicioInputSerializer(serializers.Serializer):
    """Comentario obligatorio para la cancelación administrativa."""

    comentario = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)


class FinalizarServicioInputSerializer(serializers.Serializer):
    """Comentario opcional de cierre del servicio."""

    comentario = serializers.CharField(required=False, allow_blank=True, default='')


# ─────────────────────────────────────────────────────────────
# Serializers públicos (solo lo autorizado al cliente)
# ─────────────────────────────────────────────────────────────

class HistorialPublicoSerializer(serializers.ModelSerializer):
    estado = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = HistorialServicio
        fields = ['estado', 'comentario', 'fecha']


class FotografiaPublicoSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Fotografia
        fields = ['url', 'descripcion', 'tipo', 'fecha']


class ComponentePublicoSerializer(serializers.ModelSerializer):
    """Lo que el cliente ve de un componente.

    Incluye `estado` y `fase` porque el cliente tiene derecho a saber en qué
    situación está lo que envió (RF-COT-15), y como etiqueta legible: el código
    interno (`RECHAZADO_BLOQUEANTE`) es de la empresa, no del cliente.

    NO incluye los campos de control interno: `trabajo_iniciado`,
    `fecha_inicio_trabajo`, `fecha_finalizacion`, `motivo_finalizacion`,
    `puede_continuar` ni `motivo_bloqueo`. Este serializer se mantiene aparte
    del administrativo para que ampliar la pantalla del cliente sea siempre una
    decisión explícita.
    """

    estado = serializers.CharField(source='get_estado_display', read_only=True)
    fase = serializers.CharField(source='get_fase_display', read_only=True)

    class Meta:
        model = Componente
        fields = [
            'id', 'servicio', 'tipo', 'marca', 'referencia', 'descripcion',
            'cantidad', 'estado', 'fase',
        ]
        read_only_fields = fields


class CotizacionPublicoSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source='get_tipo_display', read_only=True)
    estado = serializers.CharField(source='get_estado_display', read_only=True)
    detalles = DetalleCotizacionSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cotizacion
        fields = ['numero', 'tipo', 'descripcion', 'estado', 'total', 'detalles']

    def get_total(self, obj):
        return str(obj.total)


class ServicioPublicoSerializer(serializers.ModelSerializer):
    tipo_servicio = serializers.CharField(source='get_tipo_servicio_display', read_only=True)
    estado = serializers.CharField(source='get_estado_display', read_only=True)
    componentes = ComponentePublicoSerializer(many=True, read_only=True)
    historial = serializers.SerializerMethodField()
    fotografias = serializers.SerializerMethodField()
    cotizaciones_pendientes = serializers.SerializerMethodField()

    class Meta:
        model = Servicio
        fields = [
            'codigo', 'tipo_servicio', 'estado', 'descripcion_solicitud',
            'fecha_solicitud', 'fecha_recepcion', 'fecha_finalizacion',
            'fecha_entrega', 'componentes', 'historial', 'fotografias',
            'cotizaciones_pendientes',
        ]

    def get_historial(self, obj):
        qs = obj.historial.filter(visible_cliente=True)
        return HistorialPublicoSerializer(qs, many=True).data

    def get_fotografias(self, obj):
        qs = obj.fotografias.filter(visible_cliente=True)
        return FotografiaPublicoSerializer(qs, many=True).data

    def get_cotizaciones_pendientes(self, obj):
        qs = obj.cotizaciones.filter(estado=EstadoCotizacion.PENDIENTE)
        return CotizacionPublicoSerializer(qs, many=True).data
class ComponenteSolicitudPublicaSerializer(serializers.Serializer):
    tipo = serializers.CharField(max_length=100)
    marca = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    referencia = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    descripcion = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True, default='')
    cantidad = serializers.IntegerField(min_value=1, default=1)


# Formatos y topes de las fotografías de la solicitud pública (RF-5).
# Se validan por extensión y no se inspecciona el contenido: la spec §6 deja
# fuera de alcance la validación del contenido de la imagen (un archivo con
# extensión de imagen y contenido dañado es responsabilidad de la empresa
# descartarlo). No se usa `ImageField` ni Pillow (plan D-9).
FOTOGRAFIA_FORMATOS = ('jpg', 'jpeg', 'png')
FOTOGRAFIA_TAMANO_MAX = 10 * 1024 * 1024  # 10 MB por archivo (criterio 4).
FOTOGRAFIAS_MAX = 5  # RF-5.1 / RF-5.2.


class FotografiaSolicitudField(serializers.FileField):
    """Valida una fotografía de la solicitud pública (RF-5.1, RF-5.3)."""

    def to_internal_value(self, data):
        archivo = super().to_internal_value(data)
        extension = Path(archivo.name).suffix.lower().lstrip('.')
        if extension not in FOTOGRAFIA_FORMATOS:
            raise serializers.ValidationError(
                'Formato no admitido: solo se aceptan JPG, JPEG o PNG.'
            )
        if archivo.size > FOTOGRAFIA_TAMANO_MAX:
            raise serializers.ValidationError(
                'La fotografía supera el límite de 10 MB por archivo.'
            )
        return archivo


class SolicitudPublicaSerializer(serializers.Serializer):
    nombre_cliente = serializers.CharField(max_length=150)
    empresa = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')
    correo_electronico = serializers.EmailField(max_length=254)
    telefono = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')
    whatsapp = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')
    descripcion_problema = serializers.CharField(max_length=500)
    entregar_en_banco = serializers.BooleanField(required=False, default=False)
    avisar_para_coordinar = serializers.BooleanField(required=False, default=False)
    recoger = serializers.BooleanField(required=False, default=False)
    componentes = ComponenteSolicitudPublicaSerializer(many=True, allow_empty=False)
    fotografias = serializers.ListField(
        child=FotografiaSolicitudField(),
        required=False,
        allow_empty=True,
        max_length=FOTOGRAFIAS_MAX,
        default=list,
        error_messages={
            'max_length': (
                'Puedes adjuntar como máximo 5 fotografías por solicitud.'
            ),
        },
    )
    idempotency_key = serializers.CharField(max_length=100, required=False, allow_blank=True)
    confirmar = serializers.BooleanField(required=False, default=False)

    def validate_correo_electronico(self, value):
        from . import validators
        return validators.normalizar_correo(value)

    def validate_telefono(self, value):
        from . import validators
        return validators.normalizar_telefono(value) if value else ''

    def validate_whatsapp(self, value):
        from . import validators
        return validators.normalizar_telefono(value) if value else ''

    def validate(self, attrs):
        if not attrs.get('telefono') and not attrs.get('whatsapp'):
            raise serializers.ValidationError({
                'telefono': ['Indica un teléfono o un WhatsApp para poder contactarte.'],
            })

        return attrs
