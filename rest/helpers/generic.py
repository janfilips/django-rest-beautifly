import pusher

from ioi.game.models import Notification


def file_notification(user, module, message, send_email=False):

    # XXX TODO check on what notifications to fire up for what users

    Notification.objects.create(user=user, module=module, message=message)

    return True
