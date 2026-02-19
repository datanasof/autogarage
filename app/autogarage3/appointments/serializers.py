
from rest_framework import serializers
from .models import Appointment
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('id','provider','user','service','start_datetime','end_datetime','status','source','notes')
        read_only_fields=('status','source','user')
    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.user
        validated_data['source'] = 'end_user'
        return super().create(validated_data)
class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta: model=Appointment; fields=('status',)
