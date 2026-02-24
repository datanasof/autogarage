
from rest_framework import serializers
from .models import Appointment

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
        return super().create(validated_data)

class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('status',)
