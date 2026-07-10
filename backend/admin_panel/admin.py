from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Read-only view of the AuditLog in Django's built-in admin site.

    All modification permissions are disabled to preserve the log's integrity.
    Admins can search and filter entries but cannot create, edit, or delete them.
    """

    list_display  = ('timestamp', 'admin', 'action', 'target_model', 'target_id')
    list_filter   = ('action', 'target_model')
    search_fields = ('admin__email', 'action', 'target_model')
    readonly_fields = (
        'admin', 'action', 'target_model', 'target_id', 'detail', 'timestamp'
    )
    ordering = ('-timestamp',)

    # Disable all write operations to keep the log immutable.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
