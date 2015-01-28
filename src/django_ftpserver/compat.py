"""
The `compat` module provides support for backwards compatibility
with older versions of django
"""

import django
from django.conf import settings


def get_user_model():
    if django.VERSION >= (1, 5):
        from django.contrib.auth import get_user_model
        return get_user_model()
    else:
        from django.contrib.auth.models import User
        return User


def get_user_model_path():
    return getattr(settings, 'AUTH_USER_MODEL', None) or 'auth.User'


def get_username_field():
    if django.VERSION >= (1, 5):
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        return getattr(UserModel, 'USERNAME_FIELD', 'username')
    else:
        return 'username'
