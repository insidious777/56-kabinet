from settings.repository import get_site_settings


def site_settings(request):
    return {
        'site_settings': get_site_settings()
    }
