
from django.urls import path
from .views import ProviderListView, ProviderDetailView, ProviderCalendarOpenBusyView, ProviderSlotsView
urlpatterns = [
    path('', ProviderListView.as_view(), name='provider_list'),
    path('<slug:slug>/', ProviderDetailView.as_view(), name='provider_detail'),
    path('<slug:slug>/calendar/', ProviderCalendarOpenBusyView.as_view(), name='provider_calendar'),
    path('<slug:slug>/slots/', ProviderSlotsView.as_view(), name='provider_slots'),
]
