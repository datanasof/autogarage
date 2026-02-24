
from rest_framework import serializers
from django.conf import settings
from .models import Provider, Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta: model=Service; fields=('id','name','description','price_cents','duration_minutes','is_active')

class ProviderListSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    service_names = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = ('id','company_name','slug','phone','email','address','city','latitude','longitude','description','services','service_names','image')

    def get_service_names(self, obj):
        return list(obj.services.filter(is_active=True).values_list('name', flat=True))

    def get_image(self, obj):
        if obj.image and obj.image.name:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return settings.MEDIA_URL.rstrip('/') + '/' + obj.image.name
        return None

class ProviderDetailSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = ('id','company_name','slug','phone','email','address','city','latitude','longitude','timezone','description','services','image')

    def get_services(self, obj):
        return ServiceSerializer(obj.services.filter(is_active=True), many=True).data

    def get_image(self, obj):
        if obj.image and obj.image.name:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return settings.MEDIA_URL.rstrip('/') + '/' + obj.image.name
        return None
