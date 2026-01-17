from django.dispatch import Signal
from django.test import TestCase

from django_ftpserver import signals


class SignalsDefinitionTest(TestCase):
    """Tests for signal definitions."""

    def test_connection_signals_exist(self):
        self.assertIsInstance(signals.ftp_server_started, Signal)
        self.assertIsInstance(signals.ftp_server_stopped, Signal)
        self.assertIsInstance(signals.ftp_client_connected, Signal)
        self.assertIsInstance(signals.ftp_client_disconnected, Signal)

    def test_authentication_signals_exist(self):
        self.assertIsInstance(signals.ftp_login, Signal)
        self.assertIsInstance(signals.ftp_login_failed, Signal)
        self.assertIsInstance(signals.ftp_logout, Signal)

    def test_file_transfer_signals_exist(self):
        self.assertIsInstance(signals.ftp_file_received, Signal)
        self.assertIsInstance(signals.ftp_file_sent, Signal)
        self.assertIsInstance(signals.ftp_file_received_incomplete, Signal)
        self.assertIsInstance(signals.ftp_file_sent_incomplete, Signal)

    def test_file_operation_signals_exist(self):
        self.assertIsInstance(signals.ftp_file_deleted, Signal)
        self.assertIsInstance(signals.ftp_file_renamed, Signal)
        self.assertIsInstance(signals.ftp_directory_created, Signal)
        self.assertIsInstance(signals.ftp_directory_deleted, Signal)

    def test_signal_can_connect_receiver(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_login.connect(receiver)
        try:
            signals.ftp_login.send(
                sender=self.__class__,
                handler=None,
                username="test",
                remote_ip="127.0.0.1",
            )
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0]["username"], "test")
        finally:
            signals.ftp_login.disconnect(receiver)

    def test_signal_can_disconnect_receiver(self):
        received = []

        def receiver(sender, **kwargs):
            received.append(kwargs)

        signals.ftp_login.connect(receiver)
        signals.ftp_login.disconnect(receiver)

        signals.ftp_login.send(
            sender=self.__class__,
            handler=None,
            username="test",
            remote_ip="127.0.0.1",
        )
        self.assertEqual(len(received), 0)
