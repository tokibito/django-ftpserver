try:
    import os
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
            uid = pwd.getpwnam(self.file_access_user).pw_uid
            gid = pwd.getpwnam(self.file_access_user).pw_gid
            os.setegid(gid)
            os.seteuid(uid)

        def terminate_impersonation(self, username):
            """undo user from impersonation
            """
            os.setegid(self.gid)
            os.seteuid(self.uid)
