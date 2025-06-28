from django.apps import AppConfig


class EntryExitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'entryexit'

    def ready(self):
        try: __import__(self.name, fromlist=['signals'])
        except ImportError: pass
