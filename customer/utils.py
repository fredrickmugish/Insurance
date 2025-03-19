# In customer/utils.py (create this file if it doesn't exist)

def create_notification(recipient, notification_type, title, message, related_link=None):
    """
    Create a notification for a user
    
    Args:
        recipient: The user who will receive the notification
        notification_type: Type of notification (from Notification.NOTIFICATION_TYPES)
        title: Notification title
        message: Notification message
        related_link: Optional URL to link to from the notification
    """
    from customer.models import Notification
    
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        related_link=related_link
    )
    return notification
