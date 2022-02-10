from settings.models import Settings


def get_site_settings():
    return Settings.objects.first()     # created via data migration
