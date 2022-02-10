from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.decorators import method_decorator

from common.decorators import preserve_help_text
from settings.models import Settings


@admin.register(Settings)
@method_decorator(preserve_help_text, name='formfield_for_manytomany')
class SettingsModelAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False    # created by data migration


@admin.register(LogEntry)
class LogEntryModelAdmin(admin.ModelAdmin):
    readonly_fields = ('action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message')
