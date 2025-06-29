import requests
from django.utils import timezone
import pytz

def get_client_ip(request):
    """
    Returns the client IP from the request, honoring X-Forwarded-For.
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # could be a comma-separated list; take the first
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")

class TimezoneMiddleware:
    """
    Activates a timezone in this order:
      1) request.user.profile.timezone
      2) ipapi.co lookup
      3) UTC fallback
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = None

        ip = get_client_ip(request)
        if ip:
            try:
                r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=0.5)
                data = r.json()
                tzname = data.get("timezone")  # e.g. "Europe/Berlin"
            except Exception:
                tzname = None  # on network errors or bad JSON

        # 3) activate or default to UTC
        if tzname in pytz.all_timezones:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()  # uses settings.TIME_ZONE (UTC)

        response = self.get_response(request)
        return response
