
from django.db import models
from django.conf import settings
from providers.models import Provider
from appointments.models import Appointment

class Review(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
