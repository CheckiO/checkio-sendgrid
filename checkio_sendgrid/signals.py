import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete

from sendgrid import Sendgrid

logger = logging.getLogger(__name__)


def unsubscribe(user, **kwargs):
    sendgrid_user = getattr(settings, 'SENDGRID_USERNAME', '')
    sendgrid_password = getattr(settings, 'SENDGRID_PASSWORD', '')
    sendgrid_server = Sendgrid(sendgrid_user, sendgrid_password)
    count = sendgrid_server.delete_user(settings.SENDGRID_LIST_MAIN, user.email)
    if count:
        logger.info("Email: %s was unsubscribed" % user.email)
    else:
        logger.info("Try to unsubscribe email: %s, but it was not in the database" % user.email)
post_delete.connect(unsubscribe, sender=User)


def user_post_save(user, **kwargs):
    if not user.is_active:
        unsubscribe(user)
post_save.connect(user_post_save, sender=User)
