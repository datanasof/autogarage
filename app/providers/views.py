
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from .models import Provider, BusinessHours, Service
from appointments.models import Appointment
from .serializers import ProviderListSerializer, ProviderDetailSerializer


class ProviderSlotsView(APIView):
    """Return available booking slots for a provider on a given date for a given service."""

    def get(self, request, slug):
        date_str = request.GET.get('date')
        service_id = request.GET.get('service_id')
        if not date_str or not service_id:
            return Response({'error': 'date and service_id required'}, status=400)
        try:
            day = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
        prov = get_object_or_404(Provider, slug=slug)
        try:
            svc = Service.objects.get(pk=service_id, provider=prov, is_active=True)
        except Service.DoesNotExist:
            return Response({'error': 'Service not found'}, status=404)
        w = day.weekday()
        hours = BusinessHours.objects.filter(provider=prov, weekday=w).order_by('open_time')
        slot_mins = 30
        if hours.exists():
            slot_mins = hours.first().slot_size_minutes or 30
        duration = svc.duration_minutes
        busy = list(
            Appointment.objects.filter(
                provider=prov,
                status__in=['booked', 'confirmed'],
                start_datetime__date=day,
            ).values_list('start_datetime', 'end_datetime')
        )
        slots = []
        for bh in hours:
            curr = datetime.combine(day, bh.open_time)
            end_dt = datetime.combine(day, bh.close_time)
            while curr + timedelta(minutes=duration) <= end_dt:
                slot_end = curr + timedelta(minutes=duration)
                overlap = any(
                    curr < e and slot_end > s
                    for s, e in busy
                )
                if not overlap:
                    slots.append({'start': curr.isoformat(), 'end': slot_end.isoformat()})
                curr += timedelta(minutes=slot_mins)
        return Response(slots)


class ProviderListView(generics.ListAPIView):
    queryset = Provider.objects.all().order_by('company_name')
    serializer_class = ProviderListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['company_name','slug','city']

class ProviderDetailView(generics.RetrieveAPIView):
    lookup_field = 'slug'
    queryset = Provider.objects.all()
    serializer_class = ProviderDetailSerializer

class ProviderCalendarOpenBusyView(APIView):
    def get(self, request, slug):
        start = request.GET.get('start'); end = request.GET.get('end')
        prov = Provider.objects.get(slug=slug)
        events = []
        # busy
        qs = Appointment.objects.filter(provider=prov, status__in=['booked','confirmed'])
        if start: qs = qs.filter(start_datetime__gte=start)
        if end: qs = qs.filter(start_datetime__lte=end)
        for a in qs.select_related('service'):
            events.append({'title': f"Busy: {a.service.name}", 'start': a.start_datetime.isoformat(), 'end': a.end_datetime.isoformat(), 'color':'#e11d48'})
        # open via BusinessHours
        if start and end:
            start_dt = datetime.fromisoformat(start.replace('Z','+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z','+00:00'))
            day = start_dt.date()
            while day <= end_dt.date():
                w = day.weekday()
                for bh in BusinessHours.objects.filter(provider=prov, weekday=w):
                    sdt = datetime.combine(day, bh.open_time)
                    edt = datetime.combine(day, bh.close_time)
                    events.append({'start': sdt.isoformat(), 'end': edt.isoformat(), 'display':'background', 'color':'#bbf7d0'})
                day = day + timedelta(days=1)
        return Response(events)
