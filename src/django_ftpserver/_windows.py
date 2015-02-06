from django.core import exceptions

try:
    import win32con
    import win32security
except ImportError:
    raise exceptions.ImproperlyConfigured(
        "It can't setup the personate user class. "
        "If your platform is Windows, please install pywin32.")
else:
    class WindowsPersonateUser(object):
        def __init__(self, file_access_user):
            self.file_access_user = file_access_user

        def impersonate_user(self, username, password):
            """impersonate user when operating file system
            """
            handler = win32security.LogonUser(
                username, None, password,
                win32con.LOGON32_LOGON_INTERACTIVE,
                win32con.LOGON32_PROVIDER_DEFAULT)
            win32security.ImpersonateLoggedOnUser(handler)
            handler.Close()

        def terminate_impersonation(self, username):
            """undo user from impersonation
            """
            win32security.RevertToSelf()
