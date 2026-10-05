"""Interfaz de trabajo en Django Admin.

Dos ideas gobiernan este archivo:

1. **El admin no es una puerta trasera al modelo.** Los campos de estado son de
   solo lectura (`estado`, `fase`, `trabajo_iniciado`, `motivo_finalizacion`, las
   fechas). El estado lo decide el backend (constitución principio 3); permitirlo
   escribir aquí permitiría saltarse las vistas y perder el rastro.
2. **El admin no reimplementa las reglas.** Las acciones llaman a
   `acciones.py`, el mismo módulo que usa la API. Si el admin tuviera su propia
   versión de RF-COT-05, existirían dos verdades.
"""

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import unquote

from .acciones import ErrorDeAccion, resumen_de_cierre
from .acciones import (
    corregir_finalizacion,
    finalizar_componente,
    finalizar_servicio,
    iniciar_trabajo,
    registrar_respuesta,
)
from .estados import ESTADOS_FINALIZACION, CanalRespuesta, EstadoComponente
from .models import (
    AprobacionServicio,
    Cliente,
    Componente,
    Cotizacion,
    DetalleCotizacion,
    EstadoServicio,
    Fotografia,
    HistorialComponente,
    HistorialServicio,
    ResultadoAprobacion,
    Servicio,
)


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _opciones(estados):
    """Convierte miembros de un `TextChoices` en pares (valor, etiqueta).

    `ESTADOS_FINALIZACION` es una tupla de miembros, no de pares. Un
    `ChoiceField` de Django espera pares, así que sin esto reventaría al
    dibujar el formulario.
    """
    return [(estado.value, estado.label) for estado in estados]


# ─────────────────────────────────────────────────────────────
# Inlines
# ─────────────────────────────────────────────────────────────

class ComponenteInline(admin.TabularInline):
    """Componentes del servicio con su estado y si pueden avanzar (T24).

    Las cuatro columnas de T24 (`estado`, `trabajo_iniciado`, `puede_continuar`
    y `motivo`) son de solo lectura: informan, no se editan aquí. Editar el
    estado desde el inline sería la vía más corta para saltarse RF-COT-09.
    """

    model = Componente
    extra = 0
    fields = (
        'tipo', 'marca', 'referencia', 'descripcion', 'cantidad',
        'estado', 'trabajo_iniciado', 'puede_continuar', 'motivo_bloqueo',
        'ver_en_detalle',
    )
    readonly_fields = (
        'estado', 'trabajo_iniciado', 'puede_continuar', 'motivo_bloqueo',
        'ver_en_detalle',
    )
    fieldsets = None
    show_change_link = True

    @admin.display(description='Puede continuar')
    def puede_continuar(self, obj):
        from .serializers import ComponenteSerializer
        return ComponenteSerializer(obj).data['puede_continuar']

    @admin.display(description='Motivo del bloqueo')
    def motivo_bloqueo(self, obj):
        from .serializers import ComponenteSerializer
        return ComponenteSerializer(obj).data['motivo_bloqueo'] or '—'

    @admin.display(description='Acciones')
    def ver_en_detalle(self, obj):
        if not obj.pk:
            return ''
        return format_html('<a href="{}">Abrir</a>', f'/admin/servicios/componente/{obj.pk}/change/')


class DetalleCotizacionInline(admin.TabularInline):
    model = DetalleCotizacion
    extra = 0


class CotizacionInline(admin.TabularInline):
    """Las cotizaciones se ven en el servicio; se editan en su propia página.

    Registrar la respuesta del cliente necesita un formulario con resultado,
    canal y observación, y además depende del componente. Editarlo desde el
    inline obligaría a resolver esa dependencia dentro de una tabla de resumen.
    """

    model = Cotizacion
    extra = 0
    fields = ('numero', 'tipo', 'componente', 'total', 'es_bloqueante', 'estado', 'canal')
    readonly_fields = ('numero', 'total', 'estado', 'canal', 'es_bloqueante')
    show_change_link = True


class AprobacionServicioInline(admin.TabularInline):
    """Respuestas ya registradas. Son el rastro: solo lectura (RF-COT-03)."""

    model = AprobacionServicio
    extra = 0
    can_delete = False
    readonly_fields = (
        'resultado', 'medio', 'fecha', 'usuario_registro', 'observacion', 'ip',
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


class HistorialServicioInline(admin.TabularInline):
    """Trazabilidad. No se edita a mano: la escriben las acciones."""

    model = HistorialServicio
    extra = 0
    can_delete = False
    readonly_fields = ('estado', 'comentario', 'fecha', 'usuario', 'visible_cliente')
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


class HistorialComponenteInline(admin.TabularInline):
    model = HistorialComponente
    extra = 0
    can_delete = False
    readonly_fields = ('estado_anterior', 'estado_nuevo', 'fase_registrada', 'comentario', 'fecha', 'usuario')
    fields = readonly_fields
    verbose_name_plural = 'Historial del componente'

    def has_add_permission(self, request, obj=None):
        return False


class FotografiaInline(admin.TabularInline):
    model = Fotografia
    extra = 0


# ─────────────────────────────────────────────────────────────
# Cliente
# ─────────────────────────────────────────────────────────────

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'telefono', 'whatsapp', 'email', 'ciudad')
    search_fields = ('nombre', 'empresa', 'telefono', 'email')
    list_filter = ('ciudad',)


# ─────────────────────────────────────────────────────────────
# Servicio
# ─────────────────────────────────────────────────────────────

class ResumenDeCierre(admin.ModelAdmin):
    """Panel de cierre del servicio (T27).

    Muestra siempre el `detalle` del motivo y solo habilita el botón de
    finalizar cuando `puede_finalizar` es verdadero (RF-COT-11, RF-COT-12).
    El botón es una cortesía: el backend vuelve a validar al recibirlo.
    """

    def resumen_actual(self, obj):
        resumen = resumen_de_cierre(obj)
        puede = resumen['puede_finalizar']
        clase = 'ok' if puede else 'pendiente'
        return format_html(
            '<div class="resumen-cierre {}">'
            '<strong>Cierre del servicio</strong><br>'
            '<span class="estado">{}</span><br>{}'
            '</div>',
            clase,
            'Habilitado' if puede else 'No habilitado',
            resumen['detalle'],
        )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Añade el resumen de cierre al contexto del formulario.

        El resumen se calcula en cada GET. Va en `extra_context` porque
        `changeform_view` es el punto donde el admin llama a
        `render_change_form`: `get_extra_context()` no existe en el
        `ModelAdmin` de Django (solo en algunas clases de contrib), así que
        sobrescribirlo no surtiría efecto.
        """
        extra_context = extra_context or {}
        if object_id:
            instancia = self.get_object(request, unquote(object_id))
            if instancia is not None:
                resumen = resumen_de_cierre(instancia)
                extra_context['resumen_cierre'] = resumen
                extra_context['puede_finalizar_servicio'] = resumen['puede_finalizar']
        return super().changeform_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        """Atiende el botón de finalizar servicio de la plantilla."""
        if 'finalizar_servicio' in request.POST:
            try:
                finalizar_servicio(servicio=obj, usuario=request.user)
            except ErrorDeAccion as error:
                self.message_user(request, error.detalle, level=messages.ERROR)
            else:
                self.message_user(
                    request, 'Servicio finalizado.', level=messages.SUCCESS,
                )
            return HttpResponseRedirect(
                reverse('admin:servicios_servicio_change', args=[obj.pk]),
            )
        return super().response_change(request, obj)


@admin.register(Servicio)
class ServicioAdmin(ResumenDeCierre):
    list_display = (
        'codigo', 'cliente', 'tipo_servicio', 'estado',
        'componentes_totales', 'fecha_solicitud', 'activo',
    )
    list_filter = ('estado', 'tipo_servicio', 'activo')
    search_fields = ('codigo', 'cliente__nombre', 'cliente__empresa', 'descripcion_solicitud')
    readonly_fields = ('token_seguimiento', 'fecha_solicitud', 'resumen_actual')
    fieldsets = (
        (None, {'fields': (
            'cliente', 'tipo_servicio', 'descripcion_solicitud',
            'observaciones_internas', 'activo',
        )}),
        ('Estado', {'fields': (
            'estado', 'fecha_recepcion', 'fecha_finalizacion', 'fecha_entrega',
        )}),
        ('Seguimiento del cliente', {'fields': ('token_seguimiento', 'fecha_solicitud')}),
        ('Cierre', {'fields': ('resumen_actual',)}),
    )
    inlines = [
        ComponenteInline,
        CotizacionInline,
        HistorialServicioInline,
        FotografiaInline,
    ]

    @admin.display(description='Componentes')
    def componentes_totales(self, obj):
        return obj.componentes.count()

    def get_form(self, request, obj=None, **kwargs):
        """Quita `FINALIZADO` de las opciones de estado.

        Los estados del flujo (`en_revision`, `en_reparacion`, ...) sí se ponen a
        mano: no hay acción de proceso para ellos. `FINALIZADO` es distinto:
        solo lo escribe la acción de cierre, que comprueba las reglas
        (RF-COT-11). Si estuviera en la lista, el admin podría saltarse el
        bloqueo del cierre eligiéndolo en el desplegable.
        """
        class ServicioForm(forms.ModelForm):
            estado = forms.ChoiceField(
                required=False,
                choices=[
                    (estado.value, estado.label)
                    for estado in EstadoServicio
                    if estado != EstadoServicio.FINALIZADO
                ],
                label='Estado',
            )

            class Meta:
                model = Servicio
                fields = (
                    'cliente', 'tipo_servicio', 'descripcion_solicitud',
                    'observaciones_internas', 'activo', 'estado',
                    'fecha_recepcion', 'fecha_finalizacion', 'fecha_entrega',
                )

        return ServicioForm


# ─────────────────────────────────────────────────────────────
# Cotización y la respuesta del cliente (T25)
# ─────────────────────────────────────────────────────────────

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    """Formulario de la respuesta del cliente (T25).

    El formulario pide resultado, canal y observación. No elige el canal por
    defecto (RF-COT-03): el canal es un dato de lo que pasó, no un valor que se
    pueda suponer. Al guardar, la respuesta se registra con
    `acciones.registrar_respuesta`, que es la misma función que usa la API, así
    que aquí no se puede escribir a mano un estado que el backend rechazaría.
    """

    list_display = (
        'numero', 'servicio', 'componente', 'tipo', 'total',
        'es_bloqueante', 'estado', 'canal', 'fecha_creacion',
    )
    list_filter = ('tipo', 'estado', 'es_bloqueante', 'canal')
    search_fields = ('numero', 'servicio__codigo', 'servicio__cliente__nombre')
    readonly_fields = (
        'numero', 'total', 'estado', 'canal', 'fecha_creacion',
    )
    inlines = [DetalleCotizacionInline, AprobacionServicioInline]
    fieldsets = (
        (None, {'fields': (
            'servicio', 'componente', 'tipo', 'descripcion', 'observaciones',
        )}),
        ('Estado', {'fields': ('numero', 'total', 'es_bloqueante', 'estado', 'canal', 'fecha_creacion')}),
        ('Respuesta del cliente', {'description': (
            'Registra por dónde respondió el cliente. Solo aplica a cotizaciones '
            'pendientes. El canal no tiene valor por defecto: hay que '
            'indicarlo porque es un dato de lo que ocurrió.'
        ), 'fields': ('resultado_respuesta', 'canal_respuesta', 'observacion_respuesta')}),
    )

    # Campos del formulario de respuesta. No son columnas del modelo.
    def get_form(self, request, obj=None, **kwargs):
        class CotizacionForm(forms.ModelForm):
            resultado_respuesta = forms.ChoiceField(
                required=False,
                choices=[('', '— sin respuesta —')] + list(ResultadoAprobacion.choices),
                label='Resultado',
            )
            canal_respuesta = forms.ChoiceField(
                required=False,
                choices=[('', '— sin respuesta —')] + list(CanalRespuesta.choices),
                label='Canal',
            )
            observacion_respuesta = forms.CharField(
                required=False, label='Observación',
                widget=forms.Textarea(attrs={'rows': 2}),
            )

            class Meta:
                model = Cotizacion
                fields = (
                    'servicio', 'componente', 'tipo', 'descripcion',
                    'observaciones', 'es_bloqueante',
                )

        return CotizacionForm

    def save_model(self, request, obj, form, change):
        respuesta = form.cleaned_data.get('resultado_respuesta')
        canal = form.cleaned_data.get('canal_respuesta')

        # Guarda primero lo administrativo, para que la respuesta se registre
        # sobre una cotización ya válida. Las relaciones van como objeto: los
        # `_id` esperan un entero, no la instancia que da `cleaned_data`.
        servicio = form.cleaned_data.get('servicio')
        if servicio is not None:
            obj.servicio = servicio
        componente = form.cleaned_data.get('componente')
        if componente is not None:
            obj.componente = componente
        obj.tipo = form.cleaned_data.get('tipo', obj.tipo)
        obj.descripcion = form.cleaned_data.get('descripcion', obj.descripcion)
        obj.observaciones = form.cleaned_data.get('observaciones', obj.observaciones)
        obj.es_bloqueante = form.cleaned_data.get('es_bloqueante', obj.es_bloqueante)
        obj.save()

        if not respuesta:
            return

        if not canal:
            self.message_user(
                request,
                'Indica por dónde respondió el cliente: es obligatorio.',
                level=messages.ERROR,
            )
            return
        if obj.componente_id is None:
            self.message_user(
                request,
                'Esta cotización no pertenece a un componente, así que no '
                'puede registrar la respuesta de un componente.',
                level=messages.ERROR,
            )
            return

        try:
            registrar_respuesta(
                servicio=obj.servicio,
                componente_id=obj.componente_id,
                cotizacion_id=obj.pk,
                resultado=respuesta,
                canal=canal,
                observacion=form.cleaned_data.get('observacion_respuesta', ''),
                usuario=request.user,
                ip=_client_ip(request),
            )
        except ErrorDeAccion as error:
            self.message_user(request, error.detalle, level=messages.ERROR)
            return

        self.message_user(
            request,
            'Respuesta registrada.',
            level=messages.SUCCESS,
        )

    def save_related(self, request, form, formsets, change):
        """Recalcula el total a partir de los detalles, igual que la API."""
        super().save_related(request, form, formsets, change)
        cotizacion = form.instance
        detalles = cotizacion.detalles.all()
        if detalles.exists():
            cotizacion.total = sum(
                detalle.valor * detalle.cantidad for detalle in detalles
            )
            cotizacion.save(update_fields=['total'])


# ─────────────────────────────────────────────────────────────
# Componente y sus acciones (T26)
# ─────────────────────────────────────────────────────────────

@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    """Ficha del componente con sus tres acciones de proceso (T26).

    Estado, fase, trabajo y fechas son de solo lectura (T24). Las acciones
    llamar a `acciones.py`, que vuelve a validar. El botón se muestra solo si la
    acción tiene sentido en el estado actual, pero eso es una cortesía visual:
    la garantía es el `raise` dentro de la acción.
    """

    list_display = (
        'tipo', 'servicio', 'estado', 'trabajo_iniciado',
        'puede_continuar', 'motivo_bloqueo', 'fecha_finalizacion',
    )
    list_filter = ('estado', 'fase', 'trabajo_iniciado', 'tipo', 'servicio')
    search_fields = ('tipo', 'marca', 'referencia', 'descripcion', 'servicio__codigo', 'servicio__cliente__nombre')
    inlines = [HistorialComponenteInline]

    @admin.display(boolean=True, description='Trabajo iniciado')
    def trabajo_iniciado(self, obj):
        return obj.trabajo_iniciado

    @admin.display(description='Puede continuar')
    def puede_continuar(self, obj):
        from .serializers import ComponenteSerializer
        return ComponenteSerializer(obj).data['puede_continuar']

    @admin.display(description='Motivo del bloqueo')
    def motivo_bloqueo(self, obj):
        from .serializers import ComponenteSerializer
        return ComponenteSerializer(obj).data['motivo_bloqueo'] or '—'

    # Campos de la acción de proceso (T26). No son columnas del modelo.
    accion = None
    motivo_finalizacion_accion = None
    nuevo_estado = None
    comentario_accion = None

    def get_fieldsets(self, request, obj=None):
        return (
            (None, {'fields': (
                'servicio', 'tipo', 'marca', 'referencia', 'descripcion',
                'cantidad',
            )}),
            ('Estado (solo lectura)', {'fields': (
                'estado', 'fase', 'trabajo_iniciado', 'fecha_inicio_trabajo',
                'fecha_finalizacion', 'motivo_finalizacion',
                'puede_continuar', 'motivo_bloqueo',
            ), 'description': (
                'Estos valores los decide el backend a través de las acciones. '
                'No se editan a mano para que quede siempre el rastro en el '
                'historial.'
            )}),
            ('Acción de proceso', {'description': (
                'Iniciar el desmontaje, finalizar el componente o corregir un '
                'cierre mal registrado. El botón se habilita solo si la acción '
                'tiene sentido ahora, pero al guardar el backend vuelve a '
                'comprobarlo.'
            ), 'fields': ('accion', 'motivo_finalizacion_accion', 'nuevo_estado', 'comentario_accion')}),
        )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return (
            'estado', 'fase', 'trabajo_iniciado', 'fecha_inicio_trabajo',
            'fecha_finalizacion', 'motivo_finalizacion',
            'puede_continuar', 'motivo_bloqueo',
        )

    def get_form(self, request, obj=None, **kwargs):
        class ComponenteForm(forms.ModelForm):
            accion = forms.ChoiceField(
                required=False,
                choices=[
                    ('', '— sin acción —'),
                    ('iniciar_trabajo', 'Iniciar desmontaje'),
                    ('finalizar', 'Finalizar componente'),
                    ('corregir', 'Corregir finalización'),
                ],
                label='Acción',
            )
            motivo_finalizacion_accion = forms.ChoiceField(
                required=False,
                choices=[('', '— elija —')] + _opciones(ESTADOS_FINALIZACION),
                label='Motivo de finalización',
            )
            nuevo_estado = forms.ChoiceField(
                required=False,
                choices=[('', '— elija —')] + list(EstadoComponente.choices),
                label='Nuevo estado',
            )
            comentario_accion = forms.CharField(
                required=False, label='Comentario',
                widget=forms.Textarea(attrs={'rows': 2}),
            )

            class Meta:
                model = Componente
                fields = (
                    'servicio', 'tipo', 'marca', 'referencia', 'descripcion',
                    'cantidad',
                )

        return ComponenteForm

    def save_model(self, request, obj, form, change):
        # Guarda primero lo administrativo de la pieza. Los campos de relación
        # se asignan como objeto, no como `_id`: `cleaned_data` de un
        # ModelChoiceField contiene la instancia, y meterla en `servicio_id`
        # falla al convertirla a entero al guardar.
        servicio = form.cleaned_data.get('servicio')
        if servicio is not None:
            obj.servicio = servicio
        obj.tipo = form.cleaned_data.get('tipo', obj.tipo)
        obj.marca = form.cleaned_data.get('marca', obj.marca)
        obj.referencia = form.cleaned_data.get('referencia', obj.referencia)
        obj.descripcion = form.cleaned_data.get('descripcion', obj.descripcion)
        obj.cantidad = form.cleaned_data.get('cantidad', obj.cantidad)
        obj.save()

        # Luego ejecuta la acción elegida, si la hubo.
        self._ejecutar_accion(request, obj, form)

    def _ejecutar_accion(self, request, obj, form):
        accion = form.cleaned_data.get('accion')
        if not accion:
            return
        servicio = obj.servicio
        try:
            if accion == 'iniciar_trabajo':
                iniciar_trabajo(
                    servicio=servicio, componente_id=obj.pk, usuario=request.user,
                )
                self.message_user(
                    request, 'Desmontaje iniciado.', level=messages.SUCCESS,
                )
            elif accion == 'finalizar':
                motivo = form.cleaned_data.get('motivo_finalizacion_accion')
                if not motivo:
                    self.message_user(
                        request, 'El motivo de finalización es obligatorio.',
                        level=messages.ERROR,
                    )
                    return
                finalizar_componente(
                    servicio=servicio, componente_id=obj.pk, motivo=motivo,
                    usuario=request.user,
                )
                self.message_user(
                    request, 'Componente finalizado.', level=messages.SUCCESS,
                )
            elif accion == 'corregir':
                nuevo = form.cleaned_data.get('nuevo_estado')
                if not nuevo:
                    self.message_user(
                        request, 'El nuevo estado es obligatorio.',
                        level=messages.ERROR,
                    )
                    return
                corregir_finalizacion(
                    servicio=servicio, componente_id=obj.pk, nuevo_estado=nuevo,
                    comentario=form.cleaned_data.get('comentario_accion', ''),
                    usuario=request.user,
                )
                self.message_user(
                    request, 'Corrección registrada.', level=messages.SUCCESS,
                )
        except ErrorDeAccion as error:
            self.message_user(request, error.detalle, level=messages.ERROR)


# ─────────────────────────────────────────────────────────────
# Resto de modelos (solo lectura de la trazabilidad)
# ─────────────────────────────────────────────────────────────

@admin.register(DetalleCotizacion)
class DetalleCotizacionAdmin(admin.ModelAdmin):
    list_display = ('cotizacion', 'descripcion', 'valor', 'cantidad')


@admin.register(AprobacionServicio)
class AprobacionServicioAdmin(admin.ModelAdmin):
    list_display = (
        'cotizacion', 'resultado', 'medio', 'fecha',
        'usuario_registro', 'observacion',
    )
    list_filter = ('resultado', 'medio')
    search_fields = ('cotizacion__numero', 'cotizacion__servicio__codigo')
    readonly_fields = (
        'cotizacion', 'resultado', 'medio', 'fecha',
        'usuario_registro', 'observacion', 'ip', 'fecha_registro',
    )

    def has_add_permission(self, request):
        return False


@admin.register(HistorialServicio)
class HistorialServicioAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'estado', 'fecha', 'usuario', 'visible_cliente')
    list_filter = ('estado', 'visible_cliente')
    readonly_fields = ('servicio', 'estado', 'comentario', 'fecha', 'usuario', 'visible_cliente')

    def has_add_permission(self, request):
        return False


@admin.register(Fotografia)
class FotografiaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'servicio', 'descripcion', 'visible_cliente', 'fecha', 'subida_por')
    list_filter = ('tipo', 'visible_cliente')
