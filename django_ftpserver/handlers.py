"""
FTP handlers with Django signal support.

This module provides FTP handlers that emit Django signals for various
FTP events, enabling logging and custom event processing.
"""

import logging

from pyftpdlib.handlers import FTPHandler

from django_ftpserver import signals


logger = logging.getLogger(__name__)

# TLS_FTPHandler requires pyOpenSSL
try:
    from pyftpdlib.handlers import TLS_FTPHandler

    HAS_TLS = True
except ImportError:
    TLS_FTPHandler = None
    HAS_TLS = False


class SignalEmitterMixin:
    """
    Mixin class that emits Django signals for FTP events.

    This mixin is for internal use only. Users should use
    DjangoFTPHandler or DjangoTLS_FTPHandler directly.
    """

    def on_connect(self):
        super().on_connect()
        logger.debug(
            "FTP client connected: remote_ip=%s, remote_port=%s",
            self.remote_ip,
            self.remote_port,
        )
        signals.ftp_client_connected.send(
            sender=self.__class__,
            handler=self,
            remote_ip=self.remote_ip,
            remote_port=self.remote_port,
        )

    def on_disconnect(self):
        username = getattr(self, "username", None)
        logger.debug(
            "FTP client disconnected: username=%s, remote_ip=%s",
            username,
            self.remote_ip,
        )
        signals.ftp_client_disconnected.send(
            sender=self.__class__,
            handler=self,
            username=username,
            remote_ip=self.remote_ip,
        )
        super().on_disconnect()

    def on_login(self, username):
        super().on_login(username)
        logger.debug("FTP login: username=%s, remote_ip=%s", username, self.remote_ip)
        signals.ftp_login.send(
            sender=self.__class__,
            handler=self,
            username=username,
            remote_ip=self.remote_ip,
        )

    def on_login_failed(self, username, password):
        super().on_login_failed(username, password)
        logger.debug(
            "FTP login failed: username=%s, remote_ip=%s", username, self.remote_ip
        )
        signals.ftp_login_failed.send(
            sender=self.__class__,
            handler=self,
            username=username,
            remote_ip=self.remote_ip,
        )

    def on_logout(self, username):
        super().on_logout(username)
        logger.debug("FTP logout: username=%s, remote_ip=%s", username, self.remote_ip)
        signals.ftp_logout.send(
            sender=self.__class__,
            handler=self,
            username=username,
            remote_ip=self.remote_ip,
        )

    def on_file_received(self, file):
        super().on_file_received(file)
        logger.debug(
            "FTP file received: username=%s, path=%s, remote_ip=%s",
            self.username,
            file,
            self.remote_ip,
        )
        signals.ftp_file_received.send(
            sender=self.__class__,
            handler=self,
            username=self.username,
            path=file,
            remote_ip=self.remote_ip,
        )

    def on_file_sent(self, file):
        super().on_file_sent(file)
        logger.debug(
            "FTP file sent: username=%s, path=%s, remote_ip=%s",
            self.username,
            file,
            self.remote_ip,
        )
        signals.ftp_file_sent.send(
            sender=self.__class__,
            handler=self,
            username=self.username,
            path=file,
            remote_ip=self.remote_ip,
        )

    def on_incomplete_file_received(self, file):
        super().on_incomplete_file_received(file)
        logger.debug(
            "FTP file received incomplete: username=%s, path=%s, remote_ip=%s",
            self.username,
            file,
            self.remote_ip,
        )
        signals.ftp_file_received_incomplete.send(
            sender=self.__class__,
            handler=self,
            username=self.username,
            path=file,
            remote_ip=self.remote_ip,
        )

    def on_incomplete_file_sent(self, file):
        super().on_incomplete_file_sent(file)
        logger.debug(
            "FTP file sent incomplete: username=%s, path=%s, remote_ip=%s",
            self.username,
            file,
            self.remote_ip,
        )
        signals.ftp_file_sent_incomplete.send(
            sender=self.__class__,
            handler=self,
            username=self.username,
            path=file,
            remote_ip=self.remote_ip,
        )

    def ftp_DELE(self, path):
        ftp_path = self.fs.ftp2fs(path)
        result = super().ftp_DELE(path)
        logger.debug(
            "FTP file deleted: username=%s, path=%s, remote_ip=%s",
            self.username,
            ftp_path,
            self.remote_ip,
        )
        signals.ftp_file_deleted.send(
            sender=self.__class__,
            handler=self,
            username=self.username,
            path=ftp_path,
            remote_ip=self.remote_ip,
        )
        return result

    def ftp_RNTO(self, path):
        path_from = self.fs.ftp2fs(self._rnfr)
        result = super().ftp_RNTO(path)
        path_to = self.fs.ftp2fs(path)
        logger.debug(
            "FTP file renamed: username=%s, path_from=%s, path_to=%s, remote_ip=%s",
            self.username,
            path_from,
            path_to,
            self.remote_ip,
        )
        signals.ftp_file_renamed.send(
            sender=self.__class__,
            handler=self,
            username=self.username,
            path_from=path_from,
            path_to=path_to,
            remote_ip=self.remote_ip,
        )
        return result

    def ftp_MKD(self, path):
        result = super().ftp_MKD(path)
        ftp_path = self.fs.ftp2fs(path)
        logger.debug(
            "FTP directory created: username=%s, path=%s, remote_ip=%s",
            self.username,
            ftp_path,
            self.remote_ip,
        )
        signals.ftp_directory_created.send(
            sender=self.__class__,
            handler=self,
            username=self.username,
            path=ftp_path,
            remote_ip=self.remote_ip,
        )
        return result

    def ftp_RMD(self, path):
        ftp_path = self.fs.ftp2fs(path)
        result = super().ftp_RMD(path)
        logger.debug(
            "FTP directory deleted: username=%s, path=%s, remote_ip=%s",
            self.username,
            ftp_path,
            self.remote_ip,
        )
        signals.ftp_directory_deleted.send(
            sender=self.__class__,
            handler=self,
            username=self.username,
            path=ftp_path,
            remote_ip=self.remote_ip,
        )
        return result


class DjangoFTPHandler(SignalEmitterMixin, FTPHandler):
    """FTP handler with Django signal support."""

    pass


if HAS_TLS:

    class DjangoTLS_FTPHandler(SignalEmitterMixin, TLS_FTPHandler):
        """TLS FTP handler with Django signal support."""

        pass
else:
    DjangoTLS_FTPHandler = None
