from unittest.mock import patch

import pytest
from pyftpdlib.servers import FTPServer

from django_ftpserver.server import FTPServerConfig, FTPServerRunner
from django_ftpserver import signals


class TestFTPServerConfig:
    """Tests for FTPServerConfig dataclass."""

    def test_minimal_config(self):
        """Test config with only required fields."""
        config = FTPServerConfig(host="127.0.0.1", port=2121)

        assert config.host == "127.0.0.1"
        assert config.port == 2121
        assert config.timeout is None
        assert config.passive_ports is None
        assert config.masquerade_address is None
        assert config.file_access_user is None
        assert config.certfile is None
        assert config.keyfile is None
        assert config.sendfile is None
        assert config.handler_options == {}

    def test_config_with_all_options(self):
        """Test config with all options specified."""
        config = FTPServerConfig(
            host="0.0.0.0",
            port=21,
            timeout=300,
            passive_ports=[50000, 50001, 50002],
            masquerade_address="203.0.113.1",
            file_access_user="ftpuser",
            certfile="/path/to/cert.pem",
            keyfile="/path/to/key.pem",
            sendfile=True,
            handler_options={"tls_control_required": True},
        )

        assert config.host == "0.0.0.0"
        assert config.port == 21
        assert config.timeout == 300
        assert config.passive_ports == [50000, 50001, 50002]
        assert config.masquerade_address == "203.0.113.1"
        assert config.file_access_user == "ftpuser"
        assert config.certfile == "/path/to/cert.pem"
        assert config.keyfile == "/path/to/key.pem"
        assert config.sendfile is True
        assert config.handler_options == {"tls_control_required": True}

    def test_default_server_class(self):
        """Test that server_class defaults to FTPServer."""
        config = FTPServerConfig(host="127.0.0.1", port=2121)
        assert config.server_class is FTPServer

    def test_default_handler_class_from_settings(self):
        """Test that handler_class defaults from settings."""
        config = FTPServerConfig(host="127.0.0.1", port=2121)
        assert config.handler_class == "django_ftpserver.handlers.DjangoFTPHandler"

    def test_default_authorizer_class_from_settings(self):
        """Test that authorizer_class defaults from settings."""
        config = FTPServerConfig(host="127.0.0.1", port=2121)
        assert (
            config.authorizer_class
            == "django_ftpserver.authorizers.FTPAccountAuthorizer"
        )

    def test_custom_classes(self):
        """Test config with custom class specifications."""
        config = FTPServerConfig(
            host="127.0.0.1",
            port=2121,
            server_class="custom.ServerClass",
            handler_class="custom.HandlerClass",
            authorizer_class="custom.AuthorizerClass",
            filesystem_class="custom.FilesystemClass",
        )

        assert config.server_class == "custom.ServerClass"
        assert config.handler_class == "custom.HandlerClass"
        assert config.authorizer_class == "custom.AuthorizerClass"
        assert config.filesystem_class == "custom.FilesystemClass"


class TestFTPServerRunner:
    """Tests for FTPServerRunner class."""

    def test_init(self):
        """Test runner initialization."""
        config = FTPServerConfig(host="127.0.0.1", port=2121)
        runner = FTPServerRunner(config)

        assert runner.config is config
        assert runner.server is None

    def test_create_server(self):
        """Test server creation."""
        config = FTPServerConfig(host="127.0.0.1", port=2121)
        runner = FTPServerRunner(config)

        server = runner.create_server()

        assert server is not None
        assert runner.server is server
        assert isinstance(server, FTPServer)
        # Clean up
        server.close_all()

    def test_create_server_with_timeout(self):
        """Test server creation with timeout option."""
        config = FTPServerConfig(host="127.0.0.1", port=2122, timeout=300)
        runner = FTPServerRunner(config)

        server = runner.create_server()

        assert server.handler.timeout == 300
        server.close_all()

    def test_create_server_with_passive_ports(self):
        """Test server creation with passive ports."""
        config = FTPServerConfig(
            host="127.0.0.1", port=2123, passive_ports=[50000, 50001]
        )
        runner = FTPServerRunner(config)

        server = runner.create_server()

        assert server.handler.passive_ports == [50000, 50001]
        server.close_all()

    def test_create_server_with_masquerade_address(self):
        """Test server creation with masquerade address."""
        config = FTPServerConfig(
            host="127.0.0.1", port=2124, masquerade_address="203.0.113.1"
        )
        runner = FTPServerRunner(config)

        server = runner.create_server()

        assert server.handler.masquerade_address == "203.0.113.1"
        server.close_all()

    def test_create_server_with_handler_options(self):
        """Test server creation with additional handler options."""
        config = FTPServerConfig(
            host="127.0.0.1",
            port=2125,
            handler_options={"banner": "Welcome to FTP"},
        )
        runner = FTPServerRunner(config)

        server = runner.create_server()

        assert server.handler.banner == "Welcome to FTP"
        server.close_all()

    def test_run_without_create_server_raises_error(self):
        """Test that run() raises error if server not created."""
        config = FTPServerConfig(host="127.0.0.1", port=2121)
        runner = FTPServerRunner(config)

        with pytest.raises(RuntimeError, match="Server not created"):
            runner.run()

    def test_run_sends_signals(self):
        """Test that run() sends start and stop signals."""
        config = FTPServerConfig(host="127.0.0.1", port=2126)
        runner = FTPServerRunner(config)
        runner.create_server()

        started_received = []
        stopped_received = []

        def on_started(sender, **kwargs):
            started_received.append(kwargs)

        def on_stopped(sender, **kwargs):
            stopped_received.append(kwargs)

        signals.ftp_server_started.connect(on_started)
        signals.ftp_server_stopped.connect(on_stopped)

        try:
            # Mock serve_forever to avoid blocking
            with patch.object(runner.server, "serve_forever"):
                runner.run()

            assert len(started_received) == 1
            assert started_received[0]["host"] == "127.0.0.1"
            assert started_received[0]["port"] == 2126

            assert len(stopped_received) == 1
            assert stopped_received[0]["host"] == "127.0.0.1"
            assert stopped_received[0]["port"] == 2126
        finally:
            signals.ftp_server_started.disconnect(on_started)
            signals.ftp_server_stopped.disconnect(on_stopped)
            runner.server.close_all()

    def test_run_with_custom_sender(self):
        """Test that run() uses custom sender for signals."""
        config = FTPServerConfig(host="127.0.0.1", port=2127)
        runner = FTPServerRunner(config)
        runner.create_server()

        received_senders = []

        def on_started(sender, **kwargs):
            received_senders.append(sender)

        signals.ftp_server_started.connect(on_started)

        class CustomSender:
            pass

        try:
            with patch.object(runner.server, "serve_forever"):
                runner.run(sender=CustomSender)

            assert len(received_senders) == 1
            assert received_senders[0] is CustomSender
        finally:
            signals.ftp_server_started.disconnect(on_started)
            runner.server.close_all()

    def test_run_default_sender_is_runner_class(self):
        """Test that run() uses FTPServerRunner as default sender."""
        config = FTPServerConfig(host="127.0.0.1", port=2128)
        runner = FTPServerRunner(config)
        runner.create_server()

        received_senders = []

        def on_started(sender, **kwargs):
            received_senders.append(sender)

        signals.ftp_server_started.connect(on_started)

        try:
            with patch.object(runner.server, "serve_forever"):
                runner.run()

            assert len(received_senders) == 1
            assert received_senders[0] is FTPServerRunner
        finally:
            signals.ftp_server_started.disconnect(on_started)
            runner.server.close_all()

    def test_stop_signal_sent_on_exception(self):
        """Test that stop signal is sent even if serve_forever raises."""
        config = FTPServerConfig(host="127.0.0.1", port=2129)
        runner = FTPServerRunner(config)
        runner.create_server()

        stopped_received = []

        def on_stopped(sender, **kwargs):
            stopped_received.append(kwargs)

        signals.ftp_server_stopped.connect(on_stopped)

        try:
            with patch.object(
                runner.server, "serve_forever", side_effect=KeyboardInterrupt
            ):
                with pytest.raises(KeyboardInterrupt):
                    runner.run()

            assert len(stopped_received) == 1
        finally:
            signals.ftp_server_stopped.disconnect(on_stopped)
            runner.server.close_all()
