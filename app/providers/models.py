
from django.db import models
from django.conf import settings

class Provider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_profile')
    company_name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=64, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timezone = models.CharField(max_length=64, default='Europe/Sofia')
    description = models.TextField(blank=True)
    def __str__(self):
        return f"{self.company_name} ({self.slug})"

class Service(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price_cents = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)

class BusinessHours(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='business_hours')
    weekday = models.IntegerField(choices=[(i, i) for i in range(7)])  # 0=Mon
    open_time = models.TimeField()
    close_time = models.TimeField()
    slot_size_minutes = models.PositiveIntegerField(default=30)
    buffer_before = models.PositiveIntegerField(default=0)
    buffer_after = models.PositiveIntegerField(default=0)

class TimeOff(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='time_off')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=200, blank=True)
