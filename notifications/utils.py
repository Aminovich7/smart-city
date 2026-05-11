from .models import Notification

def notify(*, user, incident=None, message, notification_type='system'):
    """Create a notification for a single user. Silently skips if user is None."""
    if user is None:
        return
    Notification.objects.create(
        user=user,
        incident=incident,
        message=message,
        notification_type=notification_type,
    )

def notify_many(*, users, incident=None, message, notification_type='system'):
    """Create notifications for multiple users at once. Skips None entries."""
    Notification.objects.bulk_create([
        Notification(
            user=user,
            incident=incident,
            message=message,
            notification_type=notification_type,
        )
        for user in users if user is not None
    ])