from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from rangefilter.filters import DateRangeQuickSelectListFilterBuilder
from more_admin_filters import ChoicesDropdownFilter, RelatedDropdownFilter
from django_admin_search_filter import get_icontains_input_filter
from src.apps.backend.models import Fingerprint


class FingerprintAdmin(admin.ModelAdmin):
    class ToolInline(admin.TabularInline):
        model = Fingerprint.tools.through
        extra = 1

    list_display = (
        'id',
        'hash',
        'kind',
        'linked_tools',
        'created_at',
        'updated_at'
    )
    list_filter = (
        ('kind', ChoicesDropdownFilter),
        ('tools', RelatedDropdownFilter),
        get_icontains_input_filter(title_='hash', attrs='hash'),
        get_icontains_input_filter(title_='value', attrs='value'),
        ('created_at', DateRangeQuickSelectListFilterBuilder()),
        ('updated_at', DateRangeQuickSelectListFilterBuilder()),
    )
    inlines = (ToolInline,)
    LINKED_TOOLS_FILTER = "fingerprints__id__exact"

    @admin.display(description="TOOLS")
    def linked_tools(self, obj):
        return format_html(
            '<a href="{}?{}={}">tools</a>',
            reverse('admin:backend_tool_changelist'),
            self.LINKED_TOOLS_FILTER,
            obj.id
        )


admin.site.register(Fingerprint, FingerprintAdmin)
