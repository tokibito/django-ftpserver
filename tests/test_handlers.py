from unittest import skipIf

from django.test import TestCase

from django_ftpserver import signals
from django_ftpserver.handlers import (
    DjangoFTPHandler,
    DjangoTLS_FTPHandler,
    SignalEmitterMixin,
    HAS_TLS,
)


class MockFS:
    """Mock filesystem for testing."""

    def ftp2fs(self, path):
        return f"/home/ftp{path}"


class MockHandler:
    """Mock handler for testing mixin behavior."""

    remote_ip = "192.168.1.1"
    remote_port = 12345
    username = "testuser"
    fs = MockFS()
    _rnfr = "/old_name.txt"

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_login(self, username):
        pass

    def on_login_failed(self, username, password):
        pass

    def on_logout(self, username):
        pass

    def on_file_received(self, file):
        pass

    def on_file_sent(self, file):
        pass

    def on_incomplete_file_received(self, file):
        pass

    def on_incomplete_file_sent(self, file):
        pass

    def ftp_DELE(self, path):
        return None

    def ftp_RNTO(self, path):
        return None

    def ftp_MKD(self, path):
        return None

    def ftp_RMD(self, path):
        return None


class TestHandler(SignalEmitterMixin, MockHandler):
    """Test handler combining mixin with mock."""
    pass


class SignalEmitterMixinTest(TestCase):
    """Tests for SignalEmitterMixin signal emissions."""

    def setUp(self):
        self.handler = TestHandler()

    def test_on_connect_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_client_connected.connect(receiver)
        try:
            self.handler.on_connect()
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
            self.assertEqual(received[0]["remote_port"], 12345)
            self.assertIs(received[0]["handler"], self.handler)
        finally:
            signals.ftp_client_connected.disconnect(receiver)

    def test_on_disconnect_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_client_disconnected.connect(receiver)
        try:
            self.handler.on_disconnect()
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
            self.assertEqual(received[0]["username"], "testuser")
        finally:
            signals.ftp_client_disconnected.disconnect(receiver)

    def test_on_login_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_login.connect(receiver)
        try:
            self.handler.on_login("testuser")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "testuser")
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
        finally:
            signals.ftp_login.disconnect(receiver)

    def test_on_login_failed_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_login_failed.connect(receiver)
        try:
            self.handler.on_login_failed("testuser", "wrongpass")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "testuser")
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
        finally:
            signals.ftp_login_failed.disconnect(receiver)

    def test_on_logout_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_logout.connect(receiver)
        try:
            self.handler.on_logout("testuser")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "testuser")
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
        finally:
            signals.ftp_logout.disconnect(receiver)

    def test_on_file_received_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_file_received.connect(receiver)
        try:
            self.handler.on_file_received("/upload/test.txt")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "testuser")
            self.assertEqual(received[0]["path"], "/upload/test.txt")
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
        finally:
            signals.ftp_file_received.disconnect(receiver)

    def test_on_file_sent_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_file_sent.connect(receiver)
        try:
            self.handler.on_file_sent("/download/test.txt")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "testuser")
            self.assertEqual(received[0]["path"], "/download/test.txt")
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
        finally:
            signals.ftp_file_sent.disconnect(receiver)

    def test_on_incomplete_file_received_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_file_received_incomplete.connect(receiver)
        try:
            self.handler.on_incomplete_file_received("/upload/partial.txt")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["path"], "/upload/partial.txt")
        finally:
            signals.ftp_file_received_incomplete.disconnect(receiver)

    def test_on_incomplete_file_sent_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_file_sent_incomplete.connect(receiver)
        try:
            self.handler.on_incomplete_file_sent("/download/partial.txt")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["path"], "/download/partial.txt")
        finally:
            signals.ftp_file_sent_incomplete.disconnect(receiver)

    def test_ftp_dele_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_file_deleted.connect(receiver)
        try:
            self.handler.ftp_DELE("/test.txt")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "testuser")
            self.assertEqual(received[0]["path"], "/home/ftp/test.txt")
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
        finally:
            signals.ftp_file_deleted.disconnect(receiver)

    def test_ftp_rnto_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_file_renamed.connect(receiver)
        try:
            self.handler.ftp_RNTO("/new_name.txt")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "testuser")
            self.assertEqual(received[0]["path_from"], "/home/ftp/old_name.txt")
            self.assertEqual(received[0]["path_to"], "/home/ftp/new_name.txt")
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
        finally:
            signals.ftp_file_renamed.disconnect(receiver)

    def test_ftp_mkd_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_directory_created.connect(receiver)
        try:
            self.handler.ftp_MKD("/newdir")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "testuser")
            self.assertEqual(received[0]["path"], "/home/ftp/newdir")
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
        finally:
            signals.ftp_directory_created.disconnect(receiver)

    def test_ftp_rmd_emits_signal(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_directory_deleted.connect(receiver)
        try:
            self.handler.ftp_RMD("/olddir")
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "testuser")
            self.assertEqual(received[0]["path"], "/home/ftp/olddir")
            self.assertEqual(received[0]["remote_ip"], "192.168.1.1")
        finally:
            signals.ftp_directory_deleted.disconnect(receiver)


class DjangoFTPHandlerTest(TestCase):
    """Tests for DjangoFTPHandler class."""

    def test_inherits_from_mixin_and_ftphandler(self):
        from pyftpdlib.handlers import FTPHandler
        self.assertTrue(issubclass(DjangoFTPHandler, SignalEmitterMixin))
        self.assertTrue(issubclass(DjangoFTPHandler, FTPHandler))

    def test_mro_mixin_before_ftphandler(self):
        mro = DjangoFTPHandler.__mro__
        mixin_index = mro.index(SignalEmitterMixin)
        from pyftpdlib.handlers import FTPHandler
        ftphandler_index = mro.index(FTPHandler)
        self.assertLess(mixin_index, ftphandler_index)


@skipIf(not HAS_TLS, "TLS support not available (pyOpenSSL not installed)")
class DjangoTLS_FTPHandlerTest(TestCase):
    """Tests for DjangoTLS_FTPHandler class."""

    def test_inherits_from_mixin_and_tls_ftphandler(self):
        from pyftpdlib.handlers import TLS_FTPHandler
        self.assertTrue(issubclass(DjangoTLS_FTPHandler, SignalEmitterMixin))
        self.assertTrue(issubclass(DjangoTLS_FTPHandler, TLS_FTPHandler))

    def test_mro_mixin_before_tls_ftphandler(self):
        mro = DjangoTLS_FTPHandler.__mro__
        mixin_index = mro.index(SignalEmitterMixin)
        from pyftpdlib.handlers import TLS_FTPHandler
        tls_ftphandler_index = mro.index(TLS_FTPHandler)
        self.assertLess(mixin_index, tls_ftphandler_index)
