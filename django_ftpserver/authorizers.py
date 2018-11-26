import os

from django.contrib.auth import authenticate
from pyftpdlib.authorizers import AuthenticationFailed

from . import models
from .compat import get_username_field


def _get_personate_user_class():
    """return personate user class
    """
    if os.name == 'nt':
        from . import _windows
        return _windows.WindowsPersonateUser
    else:
        from . import _unix
        return _unix.UnixPersonateUser


class FTPAccountAuthorizer(object):
    """Authorizer class by django authentication.
    """
    model = models.FTPUserAccount
    personate_user_class = None

    def __init__(self, file_access_user=None):
        self.username_field = get_username_field()
        if file_access_user:
            personate_user_class = (
                self.personate_user_class or _get_personate_user_class())
            self.personate_user = personate_user_class(file_access_user)
        else:
            self.personate_user = None

    def _filter_user_by(self, username):
        return {"user__%s" % self.username_field: username}

    def has_user(self, username):
        """return True if exists user.
        """
        return self.model.objects.filter(
            **self._filter_user_by(username)
        ).exists()

    def get_account(self, username):
        """return user by username.
        """
        try:
            account = self.model.objects.get(
                **self._filter_user_by(username)
            )
        except self.model.DoesNotExist:
            return None
        return account

    def validate_authentication(self, username, password, handler):
        """authenticate user with password
        """
        user = authenticate(
            **{self.username_field: username, 'password': password}
        )
        account = self.get_account(username)
        if not (user and account):
            raise AuthenticationFailed("Authentication failed.")

    def get_home_dir(self, username):
        account = self.get_account(username)
        if not account:
            return ''
        return account.get_home_dir()

    def get_msg_login(self, username):
        """message for welcome.
        """
        account = self.get_account(username)
        if account:
            account.update_last_login()
            account.save()
        return 'welcome.'

    def get_msg_quit(self, username):
        return 'good bye.'

    def has_perm(self, username, perm, path=None):
        """check user permission
        """
        account = self.get_account(username)
        return account and account.has_perm(perm, path)

    def get_perms(self, username):
        """return user permissions
        """
        account = self.get_account(username)
        return account and account.get_perms()

    def impersonate_user(self, username, password):
        """delegate to personate_user method
        """
        if self.personate_user:
            self.personate_user.impersonate_user(username, password)

    def terminate_impersonation(self, username):
        """delegate to terminate_impersonation method
        """
        if self.personate_user:
            self.personate_user.terminate_impersonation(username)
