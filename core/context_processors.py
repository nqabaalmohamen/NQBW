from .models import SiteSettings

def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
        return {'site_settings': settings}
    except Exception:
        # In case DB is not migrated yet
        return {'site_settings': None}
