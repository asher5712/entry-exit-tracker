from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def add_entry_exit_permissions(instance, created, **kwargs):
    if created: instance.user_permissions.set(
        Permission.objects.get(
            content_type__app_label__iexact='entryexit',
            content_type__model__iexact='EntryExitRecord'
        )
    )
    return
