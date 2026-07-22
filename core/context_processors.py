def site_settings(request):
    """
    Injects site_settings into all templates safely.
    Falls back to default model values if DB is unavailable or not migrated.
    """
    try:
        from .models import SiteSettings
        obj = SiteSettings.objects.first()
        if obj is None:
            obj = SiteSettings()  # unsaved instance with all field defaults
        return {'site_settings': obj}
    except Exception:
        try:
            from .models import SiteSettings
            return {'site_settings': SiteSettings()}  # All defaults, no DB needed
        except Exception:
            return {'site_settings': None}
