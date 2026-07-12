from django.shortcuts import render
from django.urls import resolve
from core.models import SiteSettings

class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Allow access to dashboard, admin, and login for staff
        if path.startswith('/dashboard/') or path.startswith('/admin/') or path.startswith('/login/'):
            return self.get_response(request)

        # Allow media and static files
        if path.startswith('/media/') or path.startswith('/static/'):
            return self.get_response(request)

        # Let staff members bypass maintenance mode
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        try:
            settings = SiteSettings.objects.first()
            if settings and settings.is_under_maintenance:
                return render(request, 'maintenance.html', {'settings': settings}, status=503)
                
            # Track site visits
            if not request.session.get('visited'):
                request.session['visited'] = True
                if settings:
                    settings.total_visits += 1
                    settings.save(update_fields=['total_visits'])
        except Exception:
            # Table might not exist yet during migrations
            pass

        return self.get_response(request)
