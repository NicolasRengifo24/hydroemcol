"""Tests de la interfaz en Django Admin (fase 6).

Comprueban dos cosas que la constitution exige por separado:

1. El admin **no** es una puerta trasera al modelo. Los campos de estado son de
   solo lectura, porque el estado lo decide el backend (constitución
   principio 3). Si el admin permitiera escribirlos, T24 serviría de atajo
   para saltarse las vistas de T16 a T20.
2. Las acciones del admin ejecutan las **mismas** reglas que la API, porque
   ambas capas llaman a `acciones.py`.
"""

from django.contrib.admin import site as admin_site
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from servicios.admin import ServicioAdmin
from servicios.estados import (
    CanalRespuesta,
    EstadoComponente,
    EstadoFaseComponente,
)
from servicios.models import (
    Cliente,
    Componente,
    Cotizacion,
    EstadoCotizacion,
    EstadoServicio,
    Servicio,
    TipoCotizacion,
)
from usuarios.models import Usuario


class BaseAdminTest(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser(
            username='admin', email='admin@hidroemcol.com', password='prueba12345',
        )
        self.client.force_login(self.admin)

        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Cilindro hidráulico',
        )

    def url_servicio(self):
        return reverse('admin:servicios_servicio_change', args=[self.servicio.pk])

    def url_componente(self):
        return reverse('admin:servicios_componente_change', args=[self.componente.pk])

    def url_cotizacion(self, cotizacion):
        return reverse('admin:servicios_cotizacion_change', args=[cotizacion.pk])

    def admin_de_url(self, url):
        """Resuelve la URL de un change del admin a su ModelAdmin."""
        partes = [p for p in url.split('/') if p]
        app_label, nombre_modelo = partes[1], partes[2]
        for registrado in admin_site._registry.values():
            meta = registrado.model._meta
            if meta.app_label == app_label and meta.model_name == nombre_modelo:
                return registrado
        raise AssertionError('No hay ModelAdmin registrado para %s' % url)

    def post_admin(self, url, **datos):
        """Haz un POST como lo haría el navegador: con los inlines incluidos.

        Django valida los formsets de los inlines aunque sean de solo lectura.
        Si sus datos de gestión no llegan en el POST, `all_valid(formsets)` es
        falso y el guardado se cancela entero: la respuesta es 200 en lugar de
        la redirección, sin que haya ningún error visible en el formulario
        principal. Por eso los tests no pueden enviar solo los campos sueltos.
        """
        registrado = self.admin_de_url(url)
        partes = [p for p in url.split('/') if p]
        instancia = registrado.model._default_manager.get(pk=partes[-2])

        for inline in registrado.inlines:
            campo_fk = next(
                campo
                for campo in inline.model._meta.fields
                if campo.is_relation
                and campo.related_model is type(instancia)
            )
            # Mismo prefijo que usa el formset del inline: el accessor del FK
            # hacia el padre, sin el `+` del accessor inverso.
            prefijo = campo_fk.remote_field.get_accessor_name(
                model=inline.model,
            ).replace('+', '')
            hijos = list(inline.model._default_manager.filter(**{campo_fk.name: instancia}))
            total = len(hijos)
            datos[f'{prefijo}-TOTAL_FORMS'] = str(total)
            datos[f'{prefijo}-INITIAL_FORMS'] = str(total)
            datos[f'{prefijo}-MIN_NUM_FORMS'] = '0'
            datos[f'{prefijo}-MAX_NUM_FORMS'] = '1000'
            for indice, hijo in enumerate(hijos):
                datos[f'{prefijo}-{indice}-id'] = str(hijo.pk)
                # Los inlines también tienen campos editables (`cantidad` en el
                # de componentes). El navegador los reenvía; si faltan, el
                # formset no valida y el guardado se cancela.
                for nombre in self.campos_editables_del_inline(inline):
                    valor = getattr(hijo, nombre, None)
                    datos[f'{prefijo}-{indice}-{nombre}'] = (
                        '' if valor is None else str(valor)
                    )

        return self.client.post(url, datos)

    def campos_editables_del_inline(self, inline):
        """Campos del inline que el admin deja escribir."""
        return [
            nombre for nombre in inline.fields
            if nombre not in inline.readonly_fields
        ]

    def mensajes_de(self, respuesta):
        """Mensajes que el admin dejó tras la redirección."""
        from django.contrib.messages import get_messages
        return [str(m) for m in get_messages(respuesta.wsgi_request)]

    def assert_accion_rechazada(self, respuesta, objeto, campo, valor):
        """Una acción que las reglas rechazan deja el objeto como estaba.

        El admin guarda el formulario, la acción falla y el error se comunica
        como mensaje antes de redirigir. Lo que importa aquí no es el código de
        respuesta, sino que el objeto no haya cambiado.
        """
        self.assertEqual(respuesta.status_code, 302)
        objeto.refresh_from_db()
        self.assertEqual(getattr(objeto, campo), valor)


# ─────────────────────────────────────────────────────────────
# T24 — El inline muestra el estado y no permite escribirlo
# ─────────────────────────────────────────────────────────────

class TestInlineDeComponentes(BaseAdminTest):
    def test_el_inline_muestra_las_cuatro_columnas(self):
        respuesta = self.client.get(self.url_servicio())
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'puede_continuar')
        self.assertContains(respuesta, 'motivo_bloqueo')

    def test_el_admin_no_permite_escribir_el_estado(self):
        """Constitución principio 3: el estado lo decide el backend."""
        self.client.post(
            self.url_componente(),
            {
                'servicio': self.servicio.pk,
                'tipo': 'Cilindro hidráulico',
                'cantidad': 1,
                'estado': EstadoComponente.FINALIZADO_POR_CLIENTE,
                'trabajo_iniciado': True,
                'motivo_finalizacion': EstadoComponente.FINALIZADO_POR_CLIENTE,
                'fecha_inicio_trabajo_0': '2026-01-01',
                'fecha_inicio_trabajo_1': '10:00:00',
                '_continue': '1',
            })
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.PENDIENTE)
        self.assertFalse(self.componente.trabajo_iniciado)
        self.assertEqual(self.componente.motivo_finalizacion, '')

    def test_el_admin_si_permite_editar_los_datos_de_la_pieza(self):
        """El estado no se escribe, pero la descripción sí."""
        self.post_admin(self.url_componente(), **{
                'servicio': self.servicio.pk,
                'tipo': 'Cilindro hidráulico',
                'marca': 'Boschrexroth',
                'referencia': 'AHS50',
                'descripcion': 'Con fuga en el pistón',
                'cantidad': 1,
                '_continue': '1',
            })
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.marca, 'Boschrexroth')
        self.assertEqual(self.componente.descripcion, 'Con fuga en el pistón')

    def test_el_estado_calculado_refleja_la_bloqueante_pendiente(self):
        """Con una bloqueante pendiente, el inline explica el bloqueo.

        El inline no ofrece un desplegable de estado: informa del estado
        calculado. Que el estado no sea escribible lo comprueba
        `test_el_admin_no_permite_escribir_el_estado`.
        """
        Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            descripcion='Repuesto',
            es_bloqueante=True,
        )
        respuesta = self.client.get(self.url_servicio())
        self.assertContains(respuesta, 'pendiente de respuesta del cliente')

    def test_el_admin_no_ofrece_finalizado_a_mano(self):
        """RF-COT-11: `FINALIZADO` solo lo escribe la acción de cierre."""
        html = self.client.get(self.url_servicio()).content.decode()
        self.assertNotIn(
            '<option value="FINALIZADO"', html,
        )


# ─────────────────────────────────────────────────────────────
# T25 — Registrar la respuesta del cliente desde la cotización
# ─────────────────────────────────────────────────────────────

class TestAccionDeRespuesta(BaseAdminTest):
    def setUp(self):
        super().setUp()
        self.cotizacion = Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            descripcion='Repuesto del cilindro',
            es_bloqueante=True,
        )

    def payload_respuesta(self, resultado=None, canal=None, observacion=''):
        """Datos válidos del formulario de cotización.

        El formulario de T25 pide también los campos del modelo, así que un POST
        que solo manda la respuesta se rechazaría por validación y la prueba
        estaría midiendo otra cosa.
        """
        datos = {
            'servicio': self.servicio.pk,
            'componente': self.componente.pk,
            'tipo': TipoCotizacion.INICIAL,
            'descripcion': 'Repuesto del cilindro',
            'observaciones': '',
            'es_bloqueante': 'on',
        }
        if resultado:
            datos['resultado_respuesta'] = resultado
        if canal:
            datos['canal_respuesta'] = canal
        if observacion:
            datos['observacion_respuesta'] = observacion
        return datos

    def test_registrar_respuesta_por_whatsapp(self):
        respuesta = self.post_admin(self.url_cotizacion(self.cotizacion), **self.payload_respuesta(
                resultado=EstadoCotizacion.APROBADA,
                canal=CanalRespuesta.WHATSAPP,
                observacion='Lo aprueba por WhatsApp'),
        )
        self.assertEqual(respuesta.status_code, 302)

        self.cotizacion.refresh_from_db()
        self.assertEqual(self.cotizacion.estado, EstadoCotizacion.APROBADA)
        self.assertEqual(self.cotizacion.canal, CanalRespuesta.WHATSAPP)

        aprobacion = self.cotizacion.aprobaciones.get()
        self.assertEqual(aprobacion.medio, CanalRespuesta.WHATSAPP)
        self.assertEqual(aprobacion.usuario_registro, self.admin)
        self.assertIsNotNone(aprobacion.fecha)

    def test_el_canal_no_tiene_valor_por_defecto(self):
        """RF-COT-03: el canal es un dato, no un supuesto."""
        html = self.client.get(self.url_cotizacion(self.cotizacion)).content.decode()
        opcion_seleccionada = (
            '<option value="WEB" selected>' in html
            or '<option value="WHATSAPP" selected>' in html
        )
        self.assertFalse(opcion_seleccionada)

    def test_sin_resultado_no_registra_nada(self):
        respuesta = self.post_admin(self.url_cotizacion(self.cotizacion), **self.payload_respuesta(canal=CanalRespuesta.WHATSAPP))
        self.assertEqual(respuesta.status_code, 302)
        self.cotizacion.refresh_from_db()
        self.assertEqual(self.cotizacion.estado, EstadoCotizacion.PENDIENTE)
        self.assertEqual(self.cotizacion.aprobaciones.count(), 0)

    def test_sin_canal_no_registra_nada(self):
        """RF-COT-03: sin canal no se puede registrar la respuesta."""
        respuesta = self.post_admin(
            self.url_cotizacion(self.cotizacion),
            **self.payload_respuesta(resultado=EstadoCotizacion.APROBADA),
        )
        self.assertEqual(respuesta.status_code, 302)
        self.cotizacion.refresh_from_db()
        self.assertEqual(self.cotizacion.estado, EstadoCotizacion.PENDIENTE)
        self.assertEqual(self.cotizacion.aprobaciones.count(), 0)
        self.assertTrue(self.mensajes_de(respuesta))

    def test_no_se_puede_responder_dos_veces(self):
        for canal in (CanalRespuesta.WEB, CanalRespuesta.WHATSAPP):
            self.post_admin(
                self.url_cotizacion(self.cotizacion),
                **self.payload_respuesta(
                    resultado=EstadoCotizacion.RECHAZADA, canal=canal,
                ),
            )
        self.cotizacion.refresh_from_db()
        self.assertEqual(self.cotizacion.aprobaciones.count(), 1)

    def test_rechazar_bloqueante_marca_el_componente(self):
        """El admin aplica la misma regla que la API (RF-COT-05)."""
        self.post_admin(
            self.url_cotizacion(self.cotizacion),
            **self.payload_respuesta(
                resultado=EstadoCotizacion.RECHAZADA,
                canal=CanalRespuesta.WHATSAPP,
            ),
        )
        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.estado, EstadoComponente.RECHAZADO_BLOQUEANTE
        )

    def test_el_admin_muestra_las_aprobaciones_registradas(self):
        self.cotizacion.estado = EstadoCotizacion.RECHAZADA
        self.cotizacion.canal = CanalRespuesta.WHATSAPP
        self.cotizacion.save()
        self.cotizacion.aprobaciones.create(
            resultado=EstadoCotizacion.RECHAZADA,
            medio=CanalRespuesta.WHATSAPP,
            fecha=timezone.now(),
            usuario_registro=self.admin,
            observacion='El cliente lo considera caro',
        )
        html = self.client.get(self.url_cotizacion(self.cotizacion)).content.decode()
        self.assertIn('El cliente lo considera caro', html)


# ─────────────────────────────────────────────────────────────
# T26 — Acciones de componente
# ─────────────────────────────────────────────────────────────

class TestAccionesDeComponente(BaseAdminTest):
    def payload_componente(self, **accion):
        """Datos válidos del formulario de componente más la acción elegida.

        Los nombres de los campos de acción (`motivo_finalizacion_accion`,
        `comentario_accion`) son los del formulario del admin, distintos de los
        de la API.
        """
        datos = {
            'servicio': self.servicio.pk,
            'tipo': 'Cilindro hidráulico',
            'cantidad': 1,
        }
        datos.update(accion)
        return datos

    def test_iniciar_desmontaje(self):
        respuesta = self.post_admin(
            self.url_componente(),
            **self.payload_componente(accion='iniciar_trabajo'),
        )
        self.assertEqual(respuesta.status_code, 302)
        self.componente.refresh_from_db()
        self.assertTrue(self.componente.trabajo_iniciado)
        self.assertEqual(
            self.componente.fase, EstadoFaseComponente.DESMONTAJE_INICIADO
        )

    def test_iniciar_desmontaje_bloqueado_no_pasa(self):
        """Con una bloqueante pendiente, el componente sigue detenido."""
        Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            descripcion='Repuesto',
            es_bloqueante=True,
        )
        respuesta = self.post_admin(
            self.url_componente(),
            **self.payload_componente(accion='iniciar_trabajo'),
        )
        self.assert_accion_rechazada(
            respuesta, self.componente, 'trabajo_iniciado', False,
        )
        self.assertTrue(self.mensajes_de(respuesta))

    def test_finalizar_componente_por_tecnico(self):
        respuesta = self.post_admin(
            self.url_componente(),
            **self.payload_componente(
                accion='finalizar',
                motivo_finalizacion_accion=EstadoComponente.FINALIZADO_POR_TECNICO,
            ),
        )
        self.assertEqual(respuesta.status_code, 302)
        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.estado, EstadoComponente.FINALIZADO_POR_TECNICO
        )
        self.assertEqual(
            self.componente.motivo_finalizacion,
            EstadoComponente.FINALIZADO_POR_TECNICO,
        )

    def test_finalizar_sin_motivo_no_pasa(self):
        respuesta = self.post_admin(
            self.url_componente(),
            **self.payload_componente(
                accion='finalizar', motivo_finalizacion_accion='',
            ),
        )
        self.assert_accion_rechazada(
            respuesta, self.componente, 'estado', EstadoComponente.PENDIENTE,
        )
        self.assertTrue(self.mensajes_de(respuesta))

    def test_finalizar_un_componente_ya_finalizado_no_pasa(self):
        self.componente.estado = EstadoComponente.FINALIZADO_POR_CLIENTE
        self.componente.save()

        respuesta = self.post_admin(
            self.url_componente(),
            **self.payload_componente(
                accion='finalizar',
                motivo_finalizacion_accion=EstadoComponente.FINALIZADO_POR_TECNICO,
            ),
        )
        self.assert_accion_rechazada(
            respuesta,
            self.componente,
            'estado',
            EstadoComponente.FINALIZADO_POR_CLIENTE,
        )

    def test_corregir_finalizacion(self):
        self.componente.estado = EstadoComponente.FINALIZADO_POR_CLIENTE
        self.componente.motivo_finalizacion = (
            EstadoComponente.FINALIZADO_POR_CLIENTE
        )
        self.componente.save()

        respuesta = self.post_admin(
            self.url_componente(),
            **self.payload_componente(
                accion='corregir',
                nuevo_estado=EstadoComponente.EN_PROCESO,
                comentario_accion='Se cerró por error',
            ),
        )
        self.assertEqual(respuesta.status_code, 302)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.EN_PROCESO)

        registro = self.componente.historial.latest('fecha')
        self.assertEqual(
            registro.estado_anterior, EstadoComponente.FINALIZADO_POR_CLIENTE
        )
        self.assertEqual(registro.usuario, self.admin)

    def test_corregir_un_componente_no_finalizado_no_pasa(self):
        respuesta = self.post_admin(
            self.url_componente(),
            **self.payload_componente(
                accion='corregir', nuevo_estado=EstadoComponente.EN_PROCESO,
            ),
        )
        self.assert_accion_rechazada(
            respuesta, self.componente, 'estado', EstadoComponente.PENDIENTE,
        )


class TestResumenDeCierreEnElAdmin(BaseAdminTest):
    def finalizar_componente(self, componente, estado=None):
        componente.estado = estado or EstadoComponente.FINALIZADO_POR_TECNICO
        componente.motivo_finalizacion = componente.estado
        componente.fecha_finalizacion = timezone.now()
        componente.save()

    def datos_validos_del_servicio(self):
        """El formulario del admin exige estos campos para poder guardar."""
        return {
            'cliente': self.cliente.pk,
            'tipo_servicio': 'REPARACION',
            'descripcion_solicitud': 'Solicitud de prueba',
            'estado': 'EN_REPARACION',
        }

    def test_el_detalle_aparece_siempre(self):
        """Con el cierre bloqueado, la interfaz explica por qué."""
        html = self.client.get(self.url_servicio()).content.decode()
        self.assertIn('sin finalizar', html)

    def test_el_boton_no_aparece_con_un_componente_sin_finalizar(self):
        html = self.client.get(self.url_servicio()).content.decode()
        self.assertNotIn('name="finalizar_servicio"', html)

    def test_el_boton_aparece_con_todos_finalizados(self):
        self.finalizar_componente(self.componente)
        html = self.client.get(self.url_servicio()).content.decode()
        self.assertIn('name="finalizar_servicio"', html)

    def test_una_bloqueante_pendiente_no_impide_que_se_ciegue_si_todo_esta_finalizado(self):
        """RF-COT-12: lo pendiente es neutro para el cierre.

        Una cotización bloqueante sin respuesta no bloquea el cierre del
        servicio. Lo que exige el cierre es que todos los componentes estén
        finalizados, y en este caso lo están.
        """
        Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            descripcion='Repuesto',
            es_bloqueante=True,
        )
        self.finalizar_componente(self.componente)
        html = self.client.get(self.url_servicio()).content.decode()
        self.assertIn('name="finalizar_servicio"', html)

    def test_un_componente_sin_finalizar_impide_el_cierre(self):
        """Con trabajo pendiente, el botón no se ofrece."""
        html = self.client.get(self.url_servicio()).content.decode()
        self.assertNotIn('name="finalizar_servicio"', html)

    def test_finalizar_servicio_desde_el_admin(self):
        self.finalizar_componente(self.componente)
        respuesta = self.post_admin(self.url_servicio(), **{**self.datos_validos_del_servicio(), 'finalizar_servicio': '1'})
        self.assertEqual(respuesta.status_code, 302)
        self.servicio.refresh_from_db()
        self.assertEqual(self.servicio.estado, EstadoServicio.FINALIZADO)

    def test_el_admin_no_cierra_un_servicio_bloqueado(self):
        """El backend vuelve a validar aunque no haya botón (T27)."""
        respuesta = self.post_admin(self.url_servicio(), **{**self.datos_validos_del_servicio(), 'finalizar_servicio': '1'})
        self.servicio.refresh_from_db()
        self.assertNotEqual(self.servicio.estado, EstadoServicio.FINALIZADO)

