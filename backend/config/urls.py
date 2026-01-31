"""
URL configuration for Photography Store.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse


def health_check(request):
    return JsonResponse({'status': 'ok'})


def robots_txt(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /\n",
        content_type="text/plain",
    )


urlpatterns = [
    path('robots.txt', robots_txt),
    path('admin/', admin.site.urls),
    path('api/health/', health_check),
    path('api/', include('apps.catalog.urls')),
    path('api/', include('apps.orders.urls')),
    path('api/', include('apps.payments.urls')),
    path('api/', include('apps.core.urls')),
    path('api/mockup/', include('apps.mockup.urls')),
    path('api/chat/', include('apps.chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
