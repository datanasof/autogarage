
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_datetime
from django.shortcuts import render
import re
from django.http import HttpResponseBadRequest
from datetime import timedelta

from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentStatusSerializer, get_or_create_slot_for_booking
from providers.models import Provider, Service
from accounts.models import User
from django.utils import timezone as tz_utils
from zoneinfo import ZoneInfo


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

class ProviderCreateAppointmentView(APIView):
    """Provider creates an arrangement for a walk-in customer (name, phone, service)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'provider_profile'):
            return Response({'error': 'Provider profile not found'}, status=403)
        provider = request.user.provider_profile
        service_id = request.data.get('service')
        start_str = request.data.get('start_datetime')
        end_str = request.data.get('end_datetime')
        customer_name = (request.data.get('customer_name') or '').strip()
        customer_phone = (request.data.get('customer_phone') or '').strip()
        customer_email = (request.data.get('customer_email') or '').strip()
        if not all([service_id, start_str, end_str, customer_name, customer_phone]):
            return Response({'error': 'service, start_datetime, end_datetime, customer_name, customer_phone required'}, status=400)
        try:
            service = Service.objects.get(pk=service_id, provider=provider, is_active=True)
        except Service.DoesNotExist:
            return Response({'error': 'Service not found'}, status=404)
        start = parse_datetime(start_str)
        end = parse_datetime(end_str)
        if not start or not end:
            return Response({'error': 'Invalid datetime format'}, status=400)
        try:
            tz = ZoneInfo(provider.timezone) if provider.timezone else ZoneInfo("UTC")
        except Exception:
            tz = ZoneInfo("UTC")
        if tz_utils.is_naive(start):
            start = tz_utils.make_aware(start, tz)
        if tz_utils.is_naive(end):
            end = tz_utils.make_aware(end, tz)
        # Get or create walk-in user (unique per phone for this provider when no email)
        if customer_email:
            try:
                user = User.objects.get(email__iexact=customer_email)
                user.first_name = customer_name or user.first_name
                user.phone = customer_phone or user.phone
                user.save(update_fields=['first_name', 'phone'])
            except User.DoesNotExist:
                user = User.objects.create(
                    username=customer_email,
                    email=customer_email,
                    first_name=customer_name,
                    phone=customer_phone,
                    role=User.Roles.END_USER,
                )
                user.set_unusable_password()
                user.save()
        else:
            safe_phone = re.sub(r'\D', '', customer_phone)[:15] or '0'
            placeholder = f"walkin-{provider.id}-{safe_phone}@autogarage.local"
            user, created = User.objects.get_or_create(
                username=placeholder,
                defaults={
                    'email': placeholder,
                    'first_name': customer_name,
                    'phone': customer_phone,
                    'role': User.Roles.END_USER,
                }
            )
            if not created:
                user.first_name = customer_name
                user.phone = customer_phone
                user.save(update_fields=['first_name', 'phone'])
        # Block if slot already has active booking
        active = Appointment.objects.filter(
            provider=provider,
            start_datetime=start,
            status__in=[Appointment.Status.BOOKED, Appointment.Status.CONFIRMED, Appointment.Status.COMPLETED],
        ).exists()
        if active:
            return Response({'error': 'This time slot is already booked.'}, status=400)
        # Reuse canceled slot if one exists (avoids unique constraint on MySQL)
        validated = {
            'user': user, 'service': service, 'end_datetime': end,
            'status': Appointment.Status.BOOKED, 'source': Appointment.Source.PROVIDER, 'notes': '',
        }
        a = get_or_create_slot_for_booking(provider, start, validated)
        if a is None:
            a = Appointment.objects.create(
                provider=provider,
                user=user,
                service=service,
                start_datetime=start,
                end_datetime=end,
                status=Appointment.Status.BOOKED,
                source=Appointment.Source.PROVIDER,
            )
        return Response(AppointmentSerializer(a).data, status=201)


class AppointmentStatusUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AppointmentSerializer
        return AppointmentStatusSerializer

    def get_queryset(self):
        qs = Appointment.objects.select_related('provider', 'user', 'service')
        user = self.request.user
        return qs.filter(user=user) | qs.filter(provider__user=user)

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
    active = Appointment.objects.filter(provider=provider, start_datetime=start, status__in=[Appointment.Status.BOOKED, Appointment.Status.CONFIRMED, Appointment.Status.COMPLETED]).exists()
    if active: return HttpResponseBadRequest('This time slot is already booked.')
    validated = {'user': request.user, 'service': service, 'end_datetime': end, 'status': Appointment.Status.BOOKED, 'source': 'end_user', 'notes': notes or ''}
    a = get_or_create_slot_for_booking(provider, start, validated)
    if a is None:
        a = Appointment.objects.create(provider=provider, user=request.user, service=service, start_datetime=start, end_datetime=end, notes=notes, status=Appointment.Status.BOOKED, source=Appointment.Source.END_USER)
    resp = render(request, 'appointments/_success.html', {'appt': a}); resp['HX-Trigger'] = 'calendar-refresh'; return resp
