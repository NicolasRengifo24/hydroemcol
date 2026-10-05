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
)

router = DefaultRouter()
router.register('clientes', ClienteViewSet, basename='cliente')
router.register('servicios', ServicioViewSet, basename='servicio')
router.register('cotizaciones', CotizacionViewSet, basename='cotizacion')

urlpatterns = [
    # Recursos anidados por servicio
    path(
        'servicios/<int:servicio_pk>/componentes/',
        ComponenteListCreateView.as_view(),
        name='servicio-componentes',
    ),
    path(
        'servicios/<int:servicio_pk>/historial/',
        HistorialServicioListCreateView.as_view(),
        name='servicio-historial',
    ),
    path(
        'servicios/<int:servicio_pk>/fotografias/',
        FotografiaListCreateView.as_view(),
        name='servicio-fotografias',
    ),
    # Recursos anidados por cotización
    path(
        'cotizaciones/<int:cotizacion_pk>/aprobaciones/',
        AprobacionListCreateView.as_view(),
        name='cotizacion-aprobaciones',
    ),
    # Acciones de proceso sobre un componente de un servicio
    path(
        'servicios/<int:servicio_pk>/componentes/<int:componente_pk>/respuesta/',
        RespuestaCotizacionView.as_view(),
        name='componente-respuesta',
    ),
    path(
        'servicios/<int:servicio_pk>/componentes/<int:componente_pk>/iniciar-trabajo/',
        IniciarTrabajoView.as_view(),
        name='componente-iniciar-trabajo',
    ),
    path(
        'servicios/<int:servicio_pk>/componentes/<int:componente_pk>/finalizar/',
        FinalizarComponenteView.as_view(),
        name='componente-finalizar',
    ),
    path(
        'servicios/<int:servicio_pk>/componentes/<int:componente_pk>/corregir-finalizacion/',
        CorregirFinalizacionView.as_view(),
        name='componente-corregir-finalizacion',
    ),
    # Cierre manual del servicio
    path(
        'servicios/<int:servicio_pk>/finalizar/',
        FinalizarServicioView.as_view(),
        name='servicio-finalizar',
    ),
    # API pública de seguimiento (token privado)
    path('seguimiento/<str:token>/', SeguimientoView.as_view(), name='seguimiento'),
    path(
        'seguimiento/<str:token>/aprobar/',
        SeguimientoAprobarView.as_view(),
        name='seguimiento-aprobar',
    ),
]

urlpatterns += router.urls