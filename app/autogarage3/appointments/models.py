
from django.db import models
from django.conf import settings
from providers.models import Provider, Service

class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED='booked','Booked'
        CONFIRMED='confirmed','Confirmed'
        COMPLETED='completed','Completed'
        CANCELED='canceled','Canceled'
    class Source(models.TextChoices):
        END_USER='end_user','End User'
        PROVIDER='provider','Provider'
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='appointments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BOOKED)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.END_USER)
    notes = models.TextField(blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['provider','start_datetime'], name='uniq_provider_start')]
