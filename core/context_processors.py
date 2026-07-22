from .models import SiteSettings

def site_settings(request):
    try:
        from django.db import connection
        # Check the column exists before accessing it
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_inquiry_open FROM core_sitesettings LIMIT 1")
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
        return {'site_settings': settings}
    except Exception:
        # Migration not applied yet — return a safe object
        class SafeSettings:
            is_inquiry_open = True
            is_institute_open = False
            slider_speed = 4000
        return {'site_settings': SafeSettings()}
