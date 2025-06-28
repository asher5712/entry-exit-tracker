from django.conf import settings
from django.db import models

# Create your models here.
class EntryExitRecord(models.Model):
    ENTRY = 'IN'
    EXIT = 'OUT'
    RECORD_TYPE_CHOICES = [
        (ENTRY, 'Entry'),
        (EXIT, 'Exit'),
    ]
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='records',
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    record_type = models.CharField(max_length=3, choices=RECORD_TYPE_CHOICES)

    def __str__(self):
        return f'{self.user.username} - {self.get_record_type_display()} at {self.timestamp}'

    class Meta:
        verbose_name_plural = 'Entry Exit Records'
        verbose_name = 'Entry Exit Record'
        ordering = ['-timestamp']
