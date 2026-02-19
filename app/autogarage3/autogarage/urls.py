
from django.contrib import admin
from django.urls import path, include
from core.views import home, public_provider, calendar_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('public-provider/', public_provider, name='public_provider'),
    path('calendar/', calendar_view, name='calendar'),

    # site routes
    path('', include('accounts.urls_site')),

    # APIs
    path('api/accounts/', include('accounts.urls')),
    path('api/providers/', include('providers.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/reviews/', include('reviews.urls')),
]
