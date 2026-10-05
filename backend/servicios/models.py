import secrets

from django.db import models
from django.utils import timezone

from servicios.estados import (
    CanalRespuesta,
    EstadoComponente,
    EstadoFaseComponente,
)
from usuarios.models import Usuario


# ─────────────────────────────────────────────────────────────
# Catálogos cerrados (definidos en el CONTEXTO_MAESTRO)
# ─────────────────────────────────────────────────────────────

class TipoServicio(models.TextChoices):
    DIAGNOSTICO = 'DIAGNOSTICO', 'Diagnóstico'
    REPARACION = 'REPARACION', 'Reparación'
    MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento'
    PRUEBA = 'PRUEBA', 'Prueba'
    OTRO = 'OTRO', 'Otro'


class EstadoServicio(models.TextChoices):
    SOLICITADO = 'SOLICITADO', 'Solicitado'
    EN_REVISION = 'EN_REVISION', 'En revisión'
    COTIZANDO = 'COTIZANDO', 'Cotizando'
    ESPERANDO_APROBACION = 'ESPERANDO_APROBACION', 'Esperando aprobación'
    EN_REPARACION = 'EN_REPARACION', 'En reparación'
    EN_PRUEBAS = 'EN_PRUEBAS', 'En pruebas'
    FINALIZADO = 'FINALIZADO', 'Finalizado'
    LISTO_PARA_ENTREGA = 'LISTO_PARA_ENTREGA', 'Listo para entrega'
    ENTREGADO = 'ENTREGADO', 'Entregado'
    NO_APROBADO = 'NO_APROBADO', 'No aprobado'
    CANCELADO = 'CANCELADO', 'Cancelado'


class TipoCotizacion(models.TextChoices):
    INICIAL = 'INICIAL', 'Inicial'
    ADICIONAL = 'ADICIONAL', 'Adicional'


class EstadoCotizacion(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    APROBADA = 'APROBADA', 'Aprobada'
    RECHAZADA = 'RECHAZADA', 'Rechazada'


class ResultadoAprobacion(models.TextChoices):
    APROBADA = 'APROBADA', 'Aprobada'
    RECHAZADA = 'RECHAZADA', 'Rechazada'


class MedioAprobacion(models.TextChoices):
    WEB = 'WEB', 'Web'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
    LLAMADA = 'LLAMADA', 'Llamada'
    PRESENCIAL = 'PRESENCIAL', 'Presencial'
    OTRO = 'OTRO', 'Otro'


class TipoFotografia(models.TextChoices):
    RECEPCION = 'RECEPCION', 'Recepción'
    DIAGNOSTICO = 'DIAGNOSTICO', 'Diagnóstico'
    REPARACION = 'REPARACION', 'Reparación'
    PRUEBA = 'PRUEBA', 'Prueba'
    OTRO = 'OTRO', 'Otro'


# ─────────────────────────────────────────────────────────────
# Entidades
# ─────────────────────────────────────────────────────────────

class Cliente(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre / contacto')
    empresa = models.CharField(max_length=200, blank=True, verbose_name='Empresa')
    telefono = models.CharField(max_length=50, blank=True, verbose_name='Teléfono')
    whatsapp = models.CharField(max_length=50, blank=True, verbose_name='WhatsApp')
    email = models.EmailField(blank=True, verbose_name='Correo')
    direccion = models.CharField(max_length=250, blank=True, verbose_name='Dirección')
    ciudad = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.empresa or self.nombre


class Servicio(models.Model):
    """Entidad central: un servicio solicitado por un cliente."""

    # DECISIÓN PENDIENTE: formato del código humano (ej. SRV-2026-00125).
    # Por ahora se deja en blanco para generar la política con el usuario.
    codigo = models.CharField(max_length=30, unique=True, blank=True, verbose_name='Código')

    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name='servicios',
        verbose_name='Cliente',
    )
    tipo_servicio = models.CharField(
        max_length=30, choices=TipoServicio.choices, verbose_name='Tipo de servicio',
    )
    estado = models.CharField(
        max_length=30, choices=EstadoServicio.choices,
        default=EstadoServicio.SOLICITADO, verbose_name='Estado',
    )
    descripcion_solicitud = models.TextField(verbose_name='Descripción de la solicitud')
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de solicitud')
    fecha_recepcion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de recepción')
    fecha_finalizacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de finalización')
    fecha_entrega = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de entrega')

    # DECISIÓN PENDIENTE: formato/longitud exacta del token. Provisional:
    # 23 bytes aleatorios seguros codificados en URL (~32 caracteres).
    token_seguimiento = models.CharField(
        max_length=64, unique=True, blank=True, verbose_name='Token de seguimiento',
    )

    observaciones_internas = models.TextField(blank=True, verbose_name='Observaciones internas')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['-fecha_solicitud']

    def _generar_codigo(self):
        """Genera SRV-<año>-<correlativo> (ej. SRV-2026-00005)."""
        anio = timezone.now().year
        ultimo = (
            Servicio.objects.filter(codigo__startswith=f'SRV-{anio}-')
            .order_by('codigo')
            .last()
        )
        consecutivo = int(ultimo.codigo.rsplit('-', 1)[-1]) + 1 if ultimo else 1
        return f'SRV-{anio}-{consecutivo:05d}'

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._generar_codigo()
        if not self.token_seguimiento:
            self.token_seguimiento = secrets.token_urlsafe(24)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo or f'Servicio #{self.pk}'


class Componente(models.Model):
    servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE, related_name='componentes',
        verbose_name='Servicio',
    )

    # DECISIÓN PENDIENTE: el documento lista tipos (cilindros, bombas, motores,
    # orbitroles, controles, válvulas, otros) pero no los define como opciones
    # cerradas. Por eso se usa texto libre por ahora.
    tipo = models.CharField(max_length=100, verbose_name='Tipo de componente')
    marca = models.CharField(max_length=100, blank=True, verbose_name='Marca')
    referencia = models.CharField(max_length=100, blank=True, verbose_name='Referencia')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    cantidad = models.PositiveIntegerField(default=1, verbose_name='Cantidad')

    # Estado del componente dentro del servicio (especificación 002). Los valores
    # vienen de `servicios/estados.py`, que es la fuente única.
    estado = models.CharField(
        max_length=30, choices=EstadoComponente.choices,
        default=EstadoComponente.PENDIENTE, verbose_name='Estado',
    )
    fase = models.CharField(
        max_length=30, choices=EstadoFaseComponente.choices,
        default=EstadoFaseComponente.RECIBIDO, verbose_name='Fase',
    )

    # El inicio de trabajo se registra al iniciar el desmontaje. Es un booleano
    # explícito y no una fase deducida, porque es el dato que decide si el
    # servicio se puede cerrar sin trabajo hecho.
    trabajo_iniciado = models.BooleanField(
        default=False, verbose_name='Trabajo iniciado',
    )
    fecha_inicio_trabajo = models.DateTimeField(
        null=True, blank=True, verbose_name='Fecha de inicio de trabajo',
    )
    fecha_finalizacion = models.DateTimeField(
        null=True, blank=True, verbose_name='Fecha de finalización',
    )
    motivo_finalizacion = models.CharField(
        max_length=30,
        choices=[
            (EstadoComponente.FINALIZADO_POR_CLIENTE, 'Finalizado por cliente'),
            (EstadoComponente.FINALIZADO_POR_TECNICO, 'Finalizado por técnico'),
        ],
        blank=True, verbose_name='Motivo de finalización',
    )

    class Meta:
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'

    def __str__(self):
        ref = f' ({self.referencia})' if self.referencia else ''
        return f'{self.tipo}{ref}'


class Cotizacion(models.Model):
    servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE, related_name='cotizaciones',
        verbose_name='Servicio',
    )

    # DECISIÓN PENDIENTE: formato del número de cotización (ej. COT-001).
    numero = models.CharField(max_length=30, unique=True, blank=True, verbose_name='Número')

    # Componente al que pertenece la cotización. Nulable a propósito: las
    # cotizaciones anteriores a la especificación 002 eran del servicio entero y
    # deben seguir siendo válidas (RF-COT-14).
    componente = models.ForeignKey(
        Componente, null=True, blank=True, on_delete=models.CASCADE,
        related_name='cotizaciones', verbose_name='Componente',
    )

    # Si es `True`, el componente queda detenido hasta que el cliente responda.
    # Booleano y no catálogo: lo decide quien cotiza, no el sistema.
    es_bloqueante = models.BooleanField(
        default=False, verbose_name='Es bloqueante',
    )

    # Canal por el que el cliente respondió esta cotización.
    canal = models.CharField(
        max_length=30, choices=CanalRespuesta.choices,
        blank=True, verbose_name='Canal de respuesta',
    )

    tipo = models.CharField(
        max_length=30, choices=TipoCotizacion.choices, default=TipoCotizacion.INICIAL,
        verbose_name='Tipo',
    )
    descripcion = models.TextField(blank=True, verbose_name='Descripción')

    # Valores en COP (ej. $850.000). Sin subtotal ni impuestos.
    total = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, verbose_name='Total',
    )

    estado = models.CharField(
        max_length=30, choices=EstadoCotizacion.choices, default=EstadoCotizacion.PENDIENTE,
        verbose_name='Estado',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    creada_por = models.ForeignKey(
        Usuario, null=True, on_delete=models.SET_NULL, related_name='cotizaciones',
        verbose_name='Creada por',
    )

    class Meta:
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
        ordering = ['-fecha_creacion']

    def _generar_numero(self):
        """Genera COT-<año>-<correlativo> (ej. COT-2026-00007)."""
        anio = timezone.now().year
        ultimo = (
            Cotizacion.objects.filter(numero__startswith=f'COT-{anio}-')
            .order_by('numero')
            .last()
        )
        consecutivo = int(ultimo.numero.rsplit('-', 1)[-1]) + 1 if ultimo else 1
        return f'COT-{anio}-{consecutivo:05d}'

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._generar_numero()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.numero or f'Cotización #{self.pk}'


class DetalleCotizacion(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion, on_delete=models.CASCADE, related_name='detalles',
        verbose_name='Cotización',
    )
    descripcion = models.CharField(max_length=300, verbose_name='Descripción del ítem')
    valor = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Valor')
    cantidad = models.PositiveIntegerField(default=1, verbose_name='Cantidad')

    class Meta:
        verbose_name = 'Detalle de cotización'
        verbose_name_plural = 'Detalles de cotización'

    def __str__(self):
        return self.descripcion


class AprobacionServicio(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion, on_delete=models.CASCADE, related_name='aprobaciones',
        verbose_name='Cotización',
    )
    resultado = models.CharField(
        max_length=30, choices=ResultadoAprobacion.choices, verbose_name='Resultado',
    )
    medio = models.CharField(
        max_length=30, choices=MedioAprobacion.choices, verbose_name='Medio',
    )
    fecha = models.DateTimeField(verbose_name='Fecha')

    # DECISIÓN PENDIENTE: una aprobación por la web (medio=WEB) no tiene usuario
    # administrativo, por eso el campo es opcional. Se definirá la convención exacta.
    usuario_registro = models.ForeignKey(
        Usuario, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='aprobaciones_registradas', verbose_name='Usuario que registró',
    )
    observacion = models.TextField(blank=True, verbose_name='Observación')
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')

    class Meta:
        verbose_name = 'Aprobación de servicio'
        verbose_name_plural = 'Aprobaciones de servicio'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f'{self.cotizacion} — {self.get_resultado_display()} ({self.get_medio_display()})'


class HistorialServicio(models.Model):
    servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE, related_name='historial',
        verbose_name='Servicio',
    )
    estado = models.CharField(
        max_length=30, choices=EstadoServicio.choices, verbose_name='Estado alcanzado',
    )
    comentario = models.TextField(blank=True, verbose_name='Comentario')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    usuario = models.ForeignKey(
        Usuario, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='historial_servicios', verbose_name='Usuario',
    )

    # Por defecto NO visible al cliente: lo interno no debe filtrarse.
    visible_cliente = models.BooleanField(default=False, verbose_name='Visible al cliente')

    class Meta:
        verbose_name = 'Historial de servicio'
        verbose_name_plural = 'Historial de servicios'
        ordering = ['fecha']

    def __str__(self):
        return f'{self.servicio} — {self.get_estado_display()}'


class HistorialComponente(models.Model):
    """Auditoría de los cambios de estado y de fase de un componente.

    Guarda el estado anterior para que una corrección de un cierre mal
    registrado quede registrada con su estado previo (RF-COT-10). Se borrará
    junto con el componente: es el rastro de su ciclo de vida, no un registro
    de auditoría de largo plazo de la empresa.
    """

    componente = models.ForeignKey(
        Componente, on_delete=models.CASCADE, related_name='historial',
        verbose_name='Componente',
    )
    estado_anterior = models.CharField(
        max_length=30, choices=EstadoComponente.choices, blank=True,
        verbose_name='Estado anterior',
    )
    estado_nuevo = models.CharField(
        max_length=30, choices=EstadoComponente.choices,
        verbose_name='Estado nuevo',
    )
    # Se llena cuando el cambio es de fase (por ejemplo al iniciar el
    # desmontaje), para poder listar el avance sin leer los estados.
    fase_registrada = models.CharField(
        max_length=30, choices=EstadoFaseComponente.choices, blank=True,
        verbose_name='Fase registrada',
    )
    comentario = models.TextField(blank=True, verbose_name='Comentario')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    usuario = models.ForeignKey(
        Usuario, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='historial_componentes', verbose_name='Usuario',
    )

    class Meta:
        verbose_name = 'Historial de componente'
        verbose_name_plural = 'Historial de componentes'
        ordering = ['fecha']

    def __str__(self):
        return f'{self.componente} — {self.estado_anterior} → {self.estado_nuevo}'


class Fotografia(models.Model):
    servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE, related_name='fotografias',
        verbose_name='Servicio',
    )
    url = models.URLField(verbose_name='URL / referencia (Cloudflare)')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    tipo = models.CharField(
        max_length=30, choices=TipoFotografia.choices, verbose_name='Tipo',
    )
    visible_cliente = models.BooleanField(default=False, verbose_name='Visible al cliente')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    subida_por = models.ForeignKey(
        Usuario, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='fotografias', verbose_name='Subida por',
    )

    class Meta:
        verbose_name = 'Fotografía'
        verbose_name_plural = 'Fotografías'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.servicio}'