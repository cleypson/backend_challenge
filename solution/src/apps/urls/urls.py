from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls import include
from django.views.generic.base import TemplateView

urlpatterns = [
    path(r'api/v1/', include('apps.api.urls')),
]

if settings.DEBUG:
    try:
        from settings.development import *
        # static/media files
        urlpatterns += static(settings.STATIC_URL,
                              document_root=settings.STATIC_ROOT)
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
    except ImportError:
        pass
