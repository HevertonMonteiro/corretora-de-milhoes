"""
URL configuration for o site da Corretora de Milhões.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("imoveis/", include("imoveis.urls")),
    path("depoimentos/", include("depoimentos.urls")),
    path("contato/", include("leads.urls")),
    path("painel/", include("painel.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
