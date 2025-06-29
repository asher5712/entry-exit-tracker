import pytz
from django.conf import settings
from django.db import models

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    timezone = models.CharField(
        max_length=32,
        choices=[(tz, tz) for tz in pytz.common_timezones],
        blank=True,  # allow empty at first
        default="UTC"  # we'll fill it in on first request
    )

    class Meta:
        verbose_name_plural = 'User Profiles'
        verbose_name = 'User Profile'
