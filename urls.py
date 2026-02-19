# autogarage/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("AutoGarage Home")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("api/", include("core.api_urls")),  # you can split per app as you have it
]