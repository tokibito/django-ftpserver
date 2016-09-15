"""
The `compat` module provides support for backwards compatibility
with older versions of django
"""

import django
from django.conf import settings


def get_user_model_path():
    return getattr(settings, 'AUTH_USER_MODEL', None) or 'auth.User'


def get_username_field():
    from django.contrib.auth import get_user_model
    UserModel = get_user_model()
    return getattr(UserModel, 'USERNAME_FIELD', 'username')


def become_daemon(*args, **kwargs):
    """become_daemon function wrapper

    In Django 1.9, 'become_daemon' is removed.
    It means compatibility.
    """
    if django.VERSION >= (1, 9):
        from .daemonize import become_daemon
    else:
        from django.utils.daemonize import become_daemon
    return become_daemon(*args, **kwargs)


try:
    string_type = basestring
except NameError:
    string_type = str
