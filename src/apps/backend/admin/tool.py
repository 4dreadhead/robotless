from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from rangefilter.filters import DateRangeQuickSelectListFilterBuilder
from more_admin_filters import RelatedDropdownFilter
from django_admin_search_filter import get_icontains_input_filter
from src.apps.backend.models import Fingerprint, Tool


class ToolAdmin(admin.ModelAdmin):
    class FingerprintInline(admin.TabularInline):
        model = Fingerprint.tools.through
        extra = 1

    list_display = (
        'id',
        'name',
        'version',
        'system',
        'linked_fingerprints',
        'created_at',
        'updated_at'
    )
    list_filter = (
        get_icontains_input_filter(title_='name', attrs='name'),
        get_icontains_input_filter(title_='version', attrs='version'),
        get_icontains_input_filter(title_='system', attrs='system'),
        ('fingerprints', RelatedDropdownFilter),
        ('created_at', DateRangeQuickSelectListFilterBuilder()),
        ('updated_at', DateRangeQuickSelectListFilterBuilder()),
    )
    inlines = (FingerprintInline,)
    LINKED_FINGERPRINTS_FILTER = "tools__id__exact"

    @admin.display(description="FINGERPRINTS")
    def linked_fingerprints(self, obj):
        return format_html(
            '<a href="{}?{}={}">fingerprints</a>',
            reverse('admin:backend_fingerprint_changelist'),
            self.LINKED_FINGERPRINTS_FILTER,
            obj.id
        )


admin.site.register(Tool, ToolAdmin)
