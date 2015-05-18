from django.conf import settings

DEFAULT_TIMEOUT = getattr(settings, 'SENDGRID_DEFAULT_TIMEOUT', 10)
USER_ADD_LIMIT = getattr(settings, 'SENDGRID_USER_ADD_LIMIT', 1000)
