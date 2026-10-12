from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AprobacionListCreateView,
    ClienteViewSet,
    ComponenteListCreateView,
    CorregirFinalizacionView,
    CotizacionViewSet,
    FinalizarComponenteView,
    FinalizarServicioView,
    FotografiaListCreateView,
    HistorialServicioListCreateView,
    IniciarTrabajoView,
    RespuestaCotizacionView,
    SeguimientoAprobarView,
    SeguimientoView,
    ServicioViewSet,
    SolicitudPublicaCreateView,
)

router = DefaultRouter()
router.register('clientes', ClienteViewSet, basename='cliente')
router.register('servicios', ServicioViewSet, basename='servicio')
router.register('cotizaciones', CotizacionViewSet, basename='cotizacion')

urlpatterns = [
    path('servicios/<int:servicio_pk>/componentes/', ComponenteListCreateView.as_view(), name='servicio-componentes'),
    path('servicios/<int:servicio_pk>/historial/', HistorialServicioListCreateView.as_view(), name='servicio-historial'),
    path('servicios/<int:servicio_pk>/fotografias/', FotografiaListCreateView.as_view(), name='servicio-fotografias'),
    path('cotizaciones/<int:cotizacion_pk>/aprobaciones/', AprobacionListCreateView.as_view(), name='cotizacion-aprobaciones'),
    path('servicios/<int:servicio_pk>/componentes/<int:componente_pk>/respuesta/', RespuestaCotizacionView.as_view(), name='componente-respuesta'),
    path('servicios/<int:servicio_pk>/componentes/<int:componente_pk>/iniciar-trabajo/', IniciarTrabajoView.as_view(), name='componente-iniciar-trabajo'),
    path('servicios/<int:servicio_pk>/componentes/<int:componente_pk>/finalizar/', FinalizarComponenteView.as_view(), name='componente-finalizar'),
    path('servicios/<int:servicio_pk>/componentes/<int:componente_pk>/corregir-finalizacion/', CorregirFinalizacionView.as_view(), name='componente-corregir-finalizacion'),
    path('servicios/<int:servicio_pk>/finalizar/', FinalizarServicioView.as_view(), name='servicio-finalizar'),
    path('seguimiento/<str:token>/', SeguimientoView.as_view(), name='seguimiento'),
    path('seguimiento/<str:token>/aprobar/', SeguimientoAprobarView.as_view(), name='seguimiento-aprobar'),
    path('solicitudes/', SolicitudPublicaCreateView.as_view(), name='solicitud-publica'),
]

urlpatterns += router.urls
