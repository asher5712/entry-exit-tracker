from django.utils import timezone
import requests
import pytz

def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get("REMOTE_ADDR", '')

class TimezoneMiddleware:
    """
    On first authenticated request with no profile.timezone:
      • call ipapi.co to get tz
      • save it into profile.timezone
    Afterwards:
      • just read profile.timezone
    Unauthenticated users fall back to UTC.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = None

        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile and profile.timezone:
                # already stored
                tzname = profile.timezone
            else:
                # first time! try IP lookup
                ip = get_client_ip(request)
                if ip:
                    try:
                        resp = requests.get(f'https://ipapi.co/{ip}/json/',
                                            timeout=0.5)
                        data = resp.json()
                        tz = data.get('timezone')
                        if tz in pytz.all_timezones:
                            tzname = tz
                            # save it for next time
                            if profile:
                                profile.timezone = tz
                                profile.save(update_fields=['timezone'])
                    except Exception:
                        pass

        # activate or fallback to UTC
        if tzname in pytz.all_timezones:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()  # uses UTC

        return self.get_response(request)
