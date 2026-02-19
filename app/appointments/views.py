
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_datetime
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from datetime import timedelta

from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentStatusSerializer
from providers.models import Provider, Service

class AppointmentCreateView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class MyAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).order_by('-start_datetime')

class ProviderAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        qs = Appointment.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(provider__user=self.request.user)
        return qs.order_by('-start_datetime')

class AppointmentStatusUpdateView(generics.UpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

class CalendarEventsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        start = request.GET.get('start'); end = request.GET.get('end')
        qs = Appointment.objects.filter(user=request.user)
        if start: qs = qs.filter(start_datetime__gte=start)
        if end: qs = qs.filter(start_datetime__lte=end)
        events=[]
        for a in qs.select_related('service','provider'):
            events.append({'id':a.id,'title':f"{a.service.name} @ {a.provider.company_name}", 'start':a.start_datetime.isoformat(), 'end':a.end_datetime.isoformat(), 'status':a.status})
        return Response(events)

class ProviderCalendarEventsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        qs = Appointment.objects.all()
        if not request.user.is_staff:
            qs = qs.filter(provider__user=request.user)
        start = request.GET.get('start'); end = request.GET.get('end')
        if start: qs = qs.filter(start_datetime__gte=start)
        if end: qs = qs.filter(start_datetime__lte=end)
        events=[{'id':a.id,'title':f"{a.service.name}", 'start':a.start_datetime.isoformat(), 'end':a.end_datetime.isoformat(), 'status':a.status} for a in qs.select_related('service','provider')]
        return Response(events)

# HTMX helpers (optional in this pack)
@login_required
def htmx_appointment_form(request):
    providers = Provider.objects.all().order_by('company_name')
    services = Service.objects.all().order_by('name')
    return render(request, 'appointments/_form.html', {'providers': providers, 'services': services})

@login_required
@require_http_methods(["POST"])
def htmx_appointment_create(request):
    provider_id = request.POST.get('provider'); service_id = request.POST.get('service'); start_str = request.POST.get('start_datetime'); notes = request.POST.get('notes','')
    if not (provider_id and service_id and start_str): return HttpResponseBadRequest('Missing fields')
    try:
        provider = Provider.objects.get(pk=provider_id); service = Service.objects.get(pk=service_id, provider=provider)
    except (Provider.DoesNotExist, Service.DoesNotExist): return HttpResponseBadRequest('Invalid provider/service')
    start = parse_datetime(start_str)
    if not start: return HttpResponseBadRequest('Invalid start datetime')
    end = start + timedelta(minutes=service.duration_minutes)
    a = Appointment.objects.create(provider=provider, user=request.user, service=service, start_datetime=start, end_datetime=end, notes=notes, status=Appointment.Status.BOOKED, source=Appointment.Source.END_USER)
    resp = render(request, 'appointments/_success.html', {'appt': a}); resp['HX-Trigger'] = 'calendar-refresh'; return resp
