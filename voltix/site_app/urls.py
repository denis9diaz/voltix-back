"""
URL configuration for site_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from apps.general.views import index
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings  # Importar configuraciones
from django.conf.urls.static import static  # Importar para servir archivos estáticos y multimedia
from apps.pdf_measurement.views import download_report
from apps.notify_service.views import NotificationListView

schema_view = get_schema_view(
   openapi.Info(
      title="Voltix API",
      default_version='v1',
      description="Documentación de la API para Voltix",
      terms_of_service="https://example.com/terms/",  # Enlace pendiente de definir
      contact=openapi.Contact(email="voltix899@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),  # Permitir acceso a todos
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),  # La ruta actual de voltix
    path("api/auth/", include("apps.authentication.urls")),
    path('api/profile/', include('apps.userprofile.urls')),
    path('users/', include('apps.users.urls')),
    path("api/invoices/", include("apps.invoices.urls")),
    path('api/measurements/', include('apps.measurements.urls')),
    path('comparations/', include('apps.comparations.urls')),
    path('api/measurements/report/download/', download_report, name='download_report'),
    # Notifications
    path('api/notifications/general/', include('apps.notifications.urls')),
    path('api/notifications/service/', include('apps.notify_service.urls')),   
    # Rutas de Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redocs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Ruta de Tesseract
    path('tesseract/', include('apps.tesseract.urls')),
]

# Configuración para servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
