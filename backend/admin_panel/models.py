from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Immutable record of every action performed by an admin user via the API.

    Design constraints:
    - Rows are NEVER updated or deleted (enforced via the admin interface and
      the absence of any update logic in admin_panel views).
    - 'admin' uses SET_NULL so the log survives if a staff account is removed.
    - 'detail' is a free-form JSON snapshot capturing the relevant object state
      at the time of the action (e.g. song title before deletion).
    """

    ACTION_CHOICES = [
        # Creator actions
        ('VERIFY_CREATOR',   'Verify Creator'),
        ('UNVERIFY_CREATOR', 'Unverify Creator'),
        ('SUSPEND_CREATOR',  'Suspend Creator'),
        ('UNSUSPEND_CREATOR','Unsuspend Creator'),
        ('DELETE_CREATOR',   'Delete Creator'),
        # Song actions
        ('APPROVE_SONG', 'Approve Song'),
        ('REJECT_SONG',  'Reject Song'),
        ('DELETE_SONG',  'Delete Song'),
        # Album actions
        ('DELETE_ALBUM', 'Delete Album'),
    ]

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        help_text="Staff user who performed the action.",
    )
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    target_model = models.CharField(
        max_length=100,
        help_text="Model class name of the affected object, e.g. 'Song'.",
    )
    target_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Primary key of the affected object at the time of the action.",
    )
    detail = models.JSONField(
        default=dict,
        blank=True,
        help_text="Contextual snapshot, e.g. {'title': 'Song Name', 'reason': '...'}.",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log Entry'
        verbose_name_plural = 'Audit Log'

    def __str__(self):
        return (
            f"[{self.timestamp:%Y-%m-%d %H:%M}] "
            f"{self.admin} → {self.action} "
            f"({self.target_model}:{self.target_id})"
        )
