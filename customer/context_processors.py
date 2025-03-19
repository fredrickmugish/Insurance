# customer/context_processors.py

def notification_processor(request):
    """Add notification data to all templates"""
    context = {
        'unread_notifications_count': 0,
        'has_unread_notifications': False
    }
    
    if request.user.is_authenticated:
        try:
            # Count unread notifications
            unread_count = request.user.notifications.filter(is_read=False).count()
            context['unread_notifications_count'] = unread_count
            context['has_unread_notifications'] = unread_count > 0
        except:
            # Handle case where notifications relation doesn't exist
            pass
    
    return context
