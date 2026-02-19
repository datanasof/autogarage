
from rest_framework import serializers
from .models import Provider, Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta: model=Service; fields=('id','name','description','price_cents','duration_minutes','is_active')

class ProviderListSerializer(serializers.ModelSerializer):
    class Meta: model=Provider; fields=('id','company_name','slug','city','latitude','longitude','description')

class ProviderDetailSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    class Meta: model=Provider; fields=('id','company_name','slug','phone','email','address','city','latitude','longitude','timezone','description','services')
