
from django.urls import path
from .views import (
    AppointmentCreateView, MyAppointmentsView, ProviderAppointmentsView, AppointmentStatusUpdateView,
    CalendarEventsView, ProviderCalendarEventsView, htmx_appointment_form, htmx_appointment_create
)

urlpatterns = [
    path('', AppointmentCreateView.as_view(), name='appointment_create'),
    path('mine/', MyAppointmentsView.as_view(), name='appointments_mine'),
    path('provider/', ProviderAppointmentsView.as_view(), name='appointments_provider'),
    path('<int:pk>/', AppointmentStatusUpdateView.as_view(), name='appointment_update'),
    path('calendar/', CalendarEventsView.as_view(), name='appointments_calendar_events'),
    path('provider-calendar/', ProviderCalendarEventsView.as_view(), name='appointments_provider_calendar'),
    path('htmx/form/', htmx_appointment_form, name='appointments_htmx_form'),
    path('htmx/create/', htmx_appointment_create, name='appointments_htmx_create'),
]
