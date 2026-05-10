from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('status_change', 'Status Change'),
        ('assignment', 'New Assignment'),
        ('resolution', 'Resolution Submitted'),
        ('feedback', 'Feedback Received'),
        ('reopened', 'Incident Reopened'),
        ('closed', 'Incident Closed'),
        ('system', 'System Alert'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    incident = models.ForeignKey(
        'incidents.Incident',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='system'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"To {self.user.username}: {self.message[:50]}"