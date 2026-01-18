"""FTP Server runner module.

This module provides classes for configuring and running an FTP server
independently of Django management commands.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Union, List, Type

from pyftpdlib.servers import FTPServer

from django_ftpserver import signals
from django_ftpserver import utils


logger = logging.getLogger(__name__)


@dataclass
class FTPServerConfig:
    """Configuration for FTP server.

    This class holds all configuration needed to create and run an FTP server.
    All options except host and port are optional.
    """

    host: str
    port: int
    # Server behavior options
    timeout: Optional[int] = None
    passive_ports: Optional[List[int]] = None
    masquerade_address: Optional[str] = None
    file_access_user: Optional[str] = None
    certfile: Optional[str] = None
    keyfile: Optional[str] = None
    sendfile: Optional[bool] = None
    # Class specifications (string path or class)
    server_class: Union[str, Type, None] = None
    handler_class: Union[str, Type, None] = None
    authorizer_class: Union[str, Type, None] = None
    filesystem_class: Union[str, Type, None] = None
    # Additional handler options (e.g., tls_control_required, tls_data_required)
    handler_options: dict = field(default_factory=dict)

    def __post_init__(self):
        """Set default values from settings if not provided."""
        if self.server_class is None:
            self.server_class = FTPServer
        if self.handler_class is None:
            self.handler_class = utils.get_ftp_setting("FTPSERVER_HANDLER")
        if self.authorizer_class is None:
            self.authorizer_class = utils.get_ftp_setting("FTPSERVER_AUTHORIZER")
        if self.filesystem_class is None:
            self.filesystem_class = utils.get_ftp_setting("FTPSERVER_FILESYSTEM")


class FTPServerRunner:
    """FTP server runner.

    This class handles creation and execution of an FTP server.
    Daemon mode and PID file management are NOT handled here;
    they should be managed by the caller (e.g., management command).
    """

    def __init__(self, config: FTPServerConfig):
        """Initialize the runner with configuration.

        :param config: FTPServerConfig instance
        """
        self.config = config
        self._server: Optional[FTPServer] = None

    def create_server(self) -> FTPServer:
        """Create and return an FTP server instance.

        :return: FTPServer instance ready to serve
        """
        config = self.config
        handler_options = dict(config.handler_options)

        # Add optional handler attributes
        if config.timeout is not None:
            handler_options["timeout"] = config.timeout
        if config.passive_ports is not None:
            handler_options["passive_ports"] = config.passive_ports
        if config.masquerade_address is not None:
            handler_options["masquerade_address"] = config.masquerade_address
        if config.certfile is not None:
            handler_options["certfile"] = config.certfile
        if config.keyfile is not None:
            handler_options["keyfile"] = config.keyfile
        if config.sendfile is not None:
            handler_options["sendfile"] = config.sendfile

        server_class = config.server_class
        if isinstance(server_class, str):
            server_class = utils.import_class(server_class)

        self._server = utils.make_server(
            server_class=server_class,
            handler_class=config.handler_class,
            authorizer_class=config.authorizer_class,
            filesystem_class=config.filesystem_class,
            host_port=(config.host, config.port),
            file_access_user=config.file_access_user,
            **handler_options,
        )
        return self._server

    @property
    def server(self) -> Optional[FTPServer]:
        """Return the current server instance."""
        return self._server

    def run(self, sender=None) -> None:
        """Run the FTP server.

        This method starts the server and blocks until the server is stopped.
        Signals are sent at server start and stop.

        :param sender: The sender for signals (e.g., Command class).
                       If None, uses FTPServerRunner class.
        """
        if self._server is None:
            raise RuntimeError("Server not created. Call create_server() first.")

        server = self._server
        config = self.config
        signal_sender = sender or self.__class__

        logger.debug("FTP server starting: host=%s, port=%s", config.host, config.port)
        signals.ftp_server_started.send(
            sender=signal_sender,
            server=server,
            host=config.host,
            port=config.port,
        )
        try:
            server.serve_forever()
        finally:
            logger.debug(
                "FTP server stopping: host=%s, port=%s", config.host, config.port
            )
            signals.ftp_server_stopped.send(
                sender=signal_sender,
                server=server,
                host=config.host,
                port=config.port,
            )
