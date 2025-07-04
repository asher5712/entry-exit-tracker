from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models import Profile


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    if created: Profile.objects.create(user=instance)
    return
