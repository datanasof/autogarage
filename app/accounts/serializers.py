from rest_framework import serializers
from .models import User
from providers.models import Provider


class ProviderProfileSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = ("id", "company_name", "slug", "phone", "email", "address", "city", "image")

    def get_image(self, obj):
        if obj.image and obj.image.name:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            from django.conf import settings
            return settings.MEDIA_URL.rstrip('/') + '/' + obj.image.name
        return None


class MeSerializer(serializers.ModelSerializer):
    provider = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role", "phone", "city", "provider")

    def get_provider(self, obj):
        if hasattr(obj, "provider_profile"):
            return ProviderProfileSerializer(
                obj.provider_profile,
                context={'request': self.context.get('request')}
            ).data
        return None
