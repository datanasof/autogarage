
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        END_USER = 'END_USER', 'End User'
        PROVIDER = 'PROVIDER', 'Provider'
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.END_USER)
    phone = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=64, blank=True)
    def __str__(self):
        return f"{self.username} ({self.role})"
