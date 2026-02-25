
from rest_framework import serializers
from django.utils import timezone
from zoneinfo import ZoneInfo

from .models import Appointment
from providers.models import Provider


class AppointmentSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.company_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Appointment
        fields = (
            'id', 'provider', 'provider_name', 'user', 'user_name', 'user_email', 'user_phone',
            'service', 'service_name', 'start_datetime', 'end_datetime', 'status', 'source', 'notes'
        )
        read_only_fields = ('status', 'source', 'user')
    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.user
        validated_data['source'] = 'end_user'
        # Interpret datetimes as provider-local time (fixes wrong timezone storage)
        # Slot times from the calendar are in provider's local time; DRF may parse
        # them as UTC. We always treat the wall-clock time as provider-local.
        provider = validated_data.get('provider')
        if provider is not None and not isinstance(provider, Provider):
            provider = Provider.objects.filter(pk=provider).first()
        if provider is not None:
            try:
                tz = ZoneInfo(provider.timezone) if provider.timezone else ZoneInfo("UTC")
            except Exception:
                tz = ZoneInfo("UTC")
            for field in ('start_datetime', 'end_datetime'):
                dt = validated_data.get(field)
                if dt is None:
                    continue
                # Get wall-clock components (year, month, day, hour, min, sec)
                if timezone.is_naive(dt):
                    dt_naive = dt
                else:
                    dt_naive = dt.replace(tzinfo=None)
                validated_data[field] = timezone.make_aware(dt_naive, tz)
        return super().create(validated_data)

class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('status',)
