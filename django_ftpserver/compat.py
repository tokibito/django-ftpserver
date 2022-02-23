"""
The `compat` module provides support for backwards compatibility
with older versions of django
"""


def get_username_field():
    from django.contrib.auth import get_user_model
    UserModel = get_user_model()
    return getattr(UserModel, 'USERNAME_FIELD', 'username')
