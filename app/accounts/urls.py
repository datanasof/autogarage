from django.urls import path
from .views import me, create_service, service_detail

urlpatterns = [
    path("me/", me, name="me"),
    path("me/services/", create_service, name="create_service"),
    path("me/services/<int:pk>/", service_detail, name="service_detail"),
]
