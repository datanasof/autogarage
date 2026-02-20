from django.contrib import admin
from django.urls import path, include
from core.views import public_provider, calendar_view, spa_view, public_config

urlpatterns = [
    path('admin/', admin.site.urls),
    path('public-provider/', public_provider, name='public_provider'),
    path('calendar/', calendar_view, name='calendar'),

    # Public config for SPA (e.g. Google Maps key)
    path('api/config/', public_config, name='public_config'),

    # APIs
    path('api/accounts/', include('accounts.urls')),
    path('api/providers/', include('providers.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/reviews/', include('reviews.urls')),

    # React SPA (catch-all for client-side routes)
    path('', spa_view),
    path('<path:path>', spa_view),
]
