
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import Provider, BusinessHours
from appointments.models import Appointment
from .serializers import ProviderListSerializer, ProviderDetailSerializer

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
            while day < end_dt.date():
                w = day.weekday()
                for bh in BusinessHours.objects.filter(provider=prov, weekday=w):
                    sdt = datetime.combine(day, bh.open_time)
                    edt = datetime.combine(day, bh.close_time)
                    events.append({'start': sdt.isoformat(), 'end': edt.isoformat(), 'display':'background', 'color':'#bbf7d0'})
                day = day + timedelta(days=1)
        return Response(events)
