from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import public_provider, calendar_view, spa_view, public_config, csrf_token_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('public-provider/', public_provider, name='public_provider'),
    path('calendar/', calendar_view, name='calendar'),

    # Media (uploaded images) – must be before SPA catch-all so /media/... is served
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),

    # Public config for SPA (e.g. Google Maps key)
    path('api/config/', public_config, name='public_config'),
    # CSRF token for SPA form submissions (sets cookie and returns token)
    path('api/csrf/', csrf_token_view, name='csrf_token'),

    # Auth (login, logout, register) – must be before SPA catch-all
    path('', include('accounts.urls_site')),

    # APIs
    path('api/accounts/', include('accounts.urls')),
    path('api/providers/', include('providers.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/reviews/', include('reviews.urls')),

    # React SPA (catch-all for client-side routes)
    path('', spa_view),
    path('<path:path>', spa_view),
]
