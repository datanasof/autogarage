
from django.urls import path
from .views_auth import login_view, logout_view, register_user_view, register_provider_view
from .views_portal import user_dashboard, provider_dashboard, edit_user_view, edit_provider_view, search_providers

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/user/', register_user_view, name='register_user'),
    path('register/provider/', register_provider_view, name='register_provider'),

    path('dashboard/user/', user_dashboard, name='user_dashboard'),
    path('dashboard/provider/', provider_dashboard, name='provider_dashboard'),
    path('edit/user/', edit_user_view, name='edit_user'),
    path('edit/provider/', edit_provider_view, name='edit_provider'),
    path('search/', search_providers, name='search_providers'),
]
