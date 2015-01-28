import os

from django.contrib.auth import authenticate
from django.core import exceptions
from pyftpdlib.authorizers import AuthenticationFailed

from . import models
from .compat import get_username_field

personate_user_class = None

try:
    import pwd
except ImportError:
    pass
else:
    class UnixPersonateUser(object):
        def __init__(self, file_access_user):
            self.file_access_user = file_access_user
            self.gid = os.getgid()
            self.uid = os.getuid()

        def impersonate_user(self, username, password):
            """impersonate user when operating file system
            """
            if self.file_access_user:
                uid = pwd.getpwnam(self.file_access_user).pw_uid
                gid = pwd.getpwnam(self.file_access_user).pw_gid
                os.setegid(gid)
                os.seteuid(uid)

        def terminate_impersonation(self, username):
            """undo user from impersonation
            """
            if self.file_access_user:
                os.setegid(self.gid)
                os.seteuid(self.uid)

    personate_user_class = UnixPersonateUser

try:
    import win32con
    import win32security
except ImportError:
    pass
else:
    class WindowsPersonateUser(object):
        def __init__(self, file_access_user):
            self.file_access_user = file_access_user

        def impersonate_user(self, username, password):
            """impersonate user when operating file system
            """
            if self.file_access_user:
                handler = win32security.LogonUser(
                    username, None, password,
                    win32con.LOGON32_LOGON_INTERACTIVE,
                    win32con.LOGON32_PROVIDER_DEFAULT)
                win32security.ImpersonateLoggedOnUser(handler)
                handler.Close()

        def terminate_impersonation(self, username):
            """undo user from impersonation
            """
            if self.file_access_user:
                win32security.RevertToSelf()

    personate_user_class = WindowsPersonateUser


if personate_user_class is None:
    raise exceptions.ImproperlyConfigured(
        "It can't setup the personate user class. "
        "If your platform is Windows, please install pywin32.")


class FTPAccountAuthorizer(personate_user_class):
    """Authorizer class by django authentication.
    """
    model = models.FTPUserAccount

    def __init__(self, file_access_user=None):
        super(FTPAccountAuthorizer, self).__init__(file_access_user)
        self.username_field = get_username_field()

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
