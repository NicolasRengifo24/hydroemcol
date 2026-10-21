from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AprobacionListCreateView,
    CambiarEstadoComponenteView,
    CancelarServicioView,
    ClienteViewSet,
    ComponenteListCreateView,
    ComponenteDetailView,
    CotizacionViewSet,
    DashboardAdministrativoView,
    DesactivarServicioView,
    FinalizarServicioView,
    FotografiaListCreateView,
    FotografiaDetailView,
    HistorialServicioListCreateView,
    RespuestaCotizacionView,
    SeguimientoAprobarView,
    SeguimientoView,
    ServicioViewSet,
    ServicioWhatsAppView,
    SolicitudPublicaCreateView,
    RegistroTecnicoView,
    RegistrarRecepcionView,
)

router = DefaultRouter()
router.register('clientes', ClienteViewSet, basename='cliente')
router.register('servicios', ServicioViewSet, basename='servicio')
router.register('cotizaciones', CotizacionViewSet, basename='cotizacion')

urlpatterns = [
    path('admin/dashboard/', DashboardAdministrativoView.as_view(), name='admin-dashboard'),
    path('servicios/<int:servicio_pk>/componentes/', ComponenteListCreateView.as_view(), name='servicio-componentes'),
    path('servicios/<int:servicio_pk>/componentes/<int:pk>/', ComponenteDetailView.as_view(), name='servicio-componente-detalle'),
    path('servicios/<int:servicio_pk>/historial/', HistorialServicioListCreateView.as_view(), name='servicio-historial'),
    path('servicios/<int:servicio_pk>/fotografias/', FotografiaListCreateView.as_view(), name='servicio-fotografias'),
    path('servicios/<int:servicio_pk>/fotografias/<int:pk>/', FotografiaDetailView.as_view(), name='servicio-fotografia-detalle'),
    path('servicios/<int:servicio_pk>/registro-tecnico/', RegistroTecnicoView.as_view(), name='servicio-registro-tecnico'),
    path('cotizaciones/<int:cotizacion_pk>/aprobaciones/', AprobacionListCreateView.as_view(), name='cotizacion-aprobaciones'),
    path('servicios/<int:servicio_pk>/componentes/<int:componente_pk>/respuesta/', RespuestaCotizacionView.as_view(), name='componente-respuesta'),
    path('servicios/<int:servicio_pk>/componentes/<int:componente_pk>/estado/', CambiarEstadoComponenteView.as_view(), name='componente-cambiar-estado'),
    path('servicios/<int:servicio_pk>/whatsapp/', ServicioWhatsAppView.as_view(), name='servicio-whatsapp'),
    path('servicios/<int:servicio_pk>/finalizar/', FinalizarServicioView.as_view(), name='servicio-finalizar'),
    path('servicios/<int:servicio_pk>/recepcion/', RegistrarRecepcionView.as_view(), name='servicio-recepcion'),
    path('servicios/<int:servicio_pk>/cancelar/', CancelarServicioView.as_view(), name='servicio-cancelar'),
    path('servicios/<int:servicio_pk>/desactivar/', DesactivarServicioView.as_view(), name='servicio-desactivar'),
    path('seguimiento/<str:token>/', SeguimientoView.as_view(), name='seguimiento'),
    path('seguimiento/<str:token>/aprobar/', SeguimientoAprobarView.as_view(), name='seguimiento-aprobar'),
    path('solicitudes/', SolicitudPublicaCreateView.as_view(), name='solicitud-publica'),
]

urlpatterns += router.urls
