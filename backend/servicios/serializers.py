from django.utils import timezone
from rest_framework import serializers

from .estados import (
    CanalRespuesta,
    ESTADOS_FINALIZACION,
    EstadoComponente,
    EstadoFaseComponente,
)
from .models import (
    AprobacionServicio,
    Cliente,
    Componente,
    Cotizacion,
    DetalleCotizacion,
    EstadoCotizacion,
    Fotografia,
    HistorialServicio,
    MedioAprobacion,
    ResultadoAprobacion,
    Servicio,
)
from .reglas import (
    componentes_no_finalizados,
    motivo_bloqueo,
    puede_continuar,
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
    puede_continuar = serializers.SerializerMethodField()
    motivo_bloqueo = serializers.SerializerMethodField()

    class Meta:
        model = Componente
        fields = [
            'id', 'servicio', 'tipo', 'marca', 'referencia', 'descripcion',
            'cantidad', 'estado', 'fase', 'trabajo_iniciado',
            'fecha_inicio_trabajo', 'fecha_finalizacion', 'motivo_finalizacion',
            'puede_continuar', 'motivo_bloqueo',
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

    def get_puede_continuar(self, obj):
        hoy = self._reglas_del_servicio(obj)
        componente = next(
            c for c in hoy['componentes'] if c['id'] == obj.pk
        )
        return puede_continuar(hoy, componente)

    def get_motivo_bloqueo(self, obj):
        hoy = self._reglas_del_servicio(obj)
        componente = next(
            c for c in hoy['componentes'] if c['id'] == obj.pk
        )
        return motivo_bloqueo(hoy, componente)


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
            # `es_bloqueante` y `canal` los decide el backend: si el cliente
            # pudiera escribirlos, podría desbloquearse a sí mismo o atribuir
            # una respuesta a un canal que no fue ese.
            'es_bloqueante',
            'canal',
        ]

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
            'descripcion_solicitud', 'fecha_solicitud', 'fecha_recepcion',
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


class FinalizarComponenteInputSerializer(serializers.Serializer):
    """Motivo de finalización de un componente (RF-COT-09)."""

    motivo = serializers.ChoiceField(choices=ESTADOS_FINALIZACION)


class CorregirFinalizacionInputSerializer(serializers.Serializer):
    """Nuevo estado tras corregir un cierre mal registrado (RF-COT-10)."""

    nuevo_estado = serializers.ChoiceField(choices=EstadoComponente.choices)
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