import logging
import os
import sys

import pyftpdlib
from pyftpdlib.servers import FTPServer

from django import get_version
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from django_ftpserver import signals
from django_ftpserver import utils
from django_ftpserver.daemonizer import become_daemon


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start FTP server"

    def add_arguments(self, parser):
        parser.add_argument("host_port", nargs="?")

        parser.add_argument(
            "--daemonize",
            action="store_true",
            dest="daemonize",
            help="become background service.",
        )
        parser.add_argument(
            "--pidfile",
            action="store",
            dest="pidfile",
            help="filename to write process id (PID).",
        )
        parser.add_argument(
            "--timeout",
            action="store",
            dest="timeout",
            type=int,
            help="timeout for remote client.",
        )
        parser.add_argument(
            "--passive-ports",
            action="store",
            dest="passive-ports",
            help="Passive ports. eg. 12345,30000-50000",
        )
        parser.add_argument(
            "--masquerade-address",
            action="store",
            dest="masquerade-address",
            help="masquerade address.",
        )
        parser.add_argument(
            "--file-access-user",
            action="store",
            dest="file-access-user",
            help="user for access to file.",
        )
        parser.add_argument(
            "--certfile", action="store", dest="certfile", help="TLS certificate file."
        )
        parser.add_argument(
            "--keyfile", action="store", dest="keyfile", help="TLS private key file."
        )
        parser.add_argument(
            "--sendfile", action="store_true", dest="sendfile", help="Use sendfile."
        )

    def make_server(
        self,
        server_class,
        handler_class,
        authorizer_class,
        filesystem_class,
        host_port,
        file_access_user=None,
        **handler_options,
    ):
        return utils.make_server(
            server_class,
            handler_class,
            authorizer_class,
            filesystem_class,
            host_port,
            file_access_user=file_access_user,
            **handler_options,
        )

    def _get_option(self, options, option_name, setting_name):
        """Get option value from command line or settings with default fallback."""
        return options.get(option_name) or utils.get_ftp_setting(setting_name)

    def _parse_host_port(self, options):
        """Parse host and port from options or settings."""
        host_port = options.get("host_port")
        if host_port:
            host, _port = host_port.split(":", 1)
            return host, int(_port)
        return (
            utils.get_ftp_setting("FTPSERVER_HOST"),
            utils.get_ftp_setting("FTPSERVER_PORT"),
        )

    def _parse_passive_ports(self, options):
        """Parse passive ports from options or settings."""
        passive_ports_str = self._get_option(
            options, "passive-ports", "FTPSERVER_PASSIVE_PORTS"
        )
        if not passive_ports_str:
            return None
        try:
            return utils.parse_ports(passive_ports_str)
        except (TypeError, ValueError):
            raise CommandError(
                "Invalid passive ports: {}".format(options["passive-ports"])
            )

    def _get_handler_class_and_options(self, certfile, keyfile):
        """Get handler class and options based on TLS configuration."""
        if certfile or keyfile:
            try:
                from pyftpdlib.handlers import TLS_FTPHandler  # noqa: F401
            except ImportError:
                raise CommandError("Can't import OpenSSL. Please install pyOpenSSL.")
            handler_class = utils.get_ftp_setting("FTPSERVER_TLSHANDLER")
            handler_options = {"tls_control_required": True, "tls_data_required": True}
        else:
            handler_class = utils.get_ftp_setting("FTPSERVER_HANDLER")
            handler_options = {}
        return handler_class, handler_options

    def _setup_daemon(self, options):
        """Setup daemon mode if enabled."""
        daemonize = self._get_option(options, "daemonize", "FTPSERVER_DAEMONIZE")
        if daemonize:
            daemonize_options = utils.get_ftp_setting("FTPSERVER_DAEMONIZE_OPTIONS")
            become_daemon(**daemonize_options)

    def _write_pidfile(self, options):
        """Write PID to file if pidfile option is set."""
        pidfile = self._get_option(options, "pidfile", "FTPSERVER_PIDFILE")
        if pidfile:
            with open(pidfile, "w") as f:
                f.write(str(os.getpid()))

    def handle(self, *args, **options):
        host, port = self._parse_host_port(options)
        passive_ports = self._parse_passive_ports(options)

        timeout = self._get_option(options, "timeout", "FTPSERVER_TIMEOUT")
        masquerade_address = self._get_option(
            options, "masquerade-address", "FTPSERVER_MASQUERADE_ADDRESS"
        )
        file_access_user = self._get_option(
            options, "file-access-user", "FTPSERVER_FILE_ACCESS_USER"
        )
        certfile = self._get_option(options, "certfile", "FTPSERVER_CERTFILE")
        keyfile = self._get_option(options, "keyfile", "FTPSERVER_KEYFILE")
        sendfile = self._get_option(options, "sendfile", "FTPSERVER_SENDFILE")

        self._setup_daemon(options)
        self._write_pidfile(options)

        handler_class, handler_options = self._get_handler_class_and_options(
            certfile, keyfile
        )
        authorizer_class = utils.get_ftp_setting("FTPSERVER_AUTHORIZER")
        filesystem_class = utils.get_ftp_setting("FTPSERVER_FILESYSTEM")

        server = self.make_server(
            server_class=FTPServer,
            handler_class=handler_class,
            authorizer_class=authorizer_class,
            filesystem_class=filesystem_class,
            host_port=(host, port),
            file_access_user=file_access_user,
            timeout=timeout,
            passive_ports=passive_ports,
            masquerade_address=masquerade_address,
            certfile=certfile,
            keyfile=keyfile,
            sendfile=sendfile,
            **handler_options,
        )

        # start server
        quit_command = "CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C"
        sys.stdout.write(
            (
                "Django version {version_dj}, using settings '{settings}'\n"
                "pyftpdlib version {version_ftp}\n"
                "Quit the server with {quit_command}.\n"
            ).format(
                version_dj=get_version(),
                version_ftp=pyftpdlib.__ver__,
                settings=settings.SETTINGS_MODULE,
                quit_command=quit_command,
            )
        )

        logger.debug("FTP server starting: host=%s, port=%s", host, port)
        signals.ftp_server_started.send(
            sender=self.__class__,
            server=server,
            host=host,
            port=port,
        )
        try:
            server.serve_forever()
        finally:
            logger.debug("FTP server stopping: host=%s, port=%s", host, port)
            signals.ftp_server_stopped.send(
                sender=self.__class__,
                server=server,
                host=host,
                port=port,
            )
