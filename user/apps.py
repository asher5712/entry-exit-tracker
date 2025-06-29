from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        try: __import__(self.name, fromlist=['signals'])
        except ImportError: pass
