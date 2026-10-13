"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from usuarios.views import CsrfView, LoginView, LogoutView, RefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Autenticación administrativa: el refresh solo viaja en cookie.
    path('api/csrf/', CsrfView.as_view(), name='csrf'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/refresh/', RefreshView.as_view(), name='refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    # API del negocio
    path('api/', include('servicios.urls')),
]

# Servir las fotografías subidas (media local) solo en desarrollo.
# En producción el almacenamiento (Cloudflare) entrega los archivos.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
