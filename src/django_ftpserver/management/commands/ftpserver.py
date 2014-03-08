import sys
import os
from optparse import make_option

import pyftpdlib
from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler

from django import get_version
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.daemonize import become_daemon

from django_ftpserver.authorizers import FTPAccountAuthorizer
from django_ftpserver import utils


class Command(BaseCommand):
    help = "Start FTP server"
    option_list = BaseCommand.option_list + (
        make_option('--daemonize', action='store_true', dest='daemonize',
                    help="become background service."),
        make_option('--pidfile', action='store', dest='pidfile',
                    help="filename to write process id (PID)."),
        make_option('--timeout', action='store', dest='timeout', type=int,
                    help="timeout for remote client."),
        make_option('--passive-ports', action='store',
                    dest='passive-ports',
                    help="Passive ports."),
        make_option('--masquerade-address', action='store',
                    dest='masquerade-address',
                    help="masquerade address."),
        make_option('--file-access-user', action='store',
                    dest='file-access-user',
                    help="user for access to file."),
    )
    args = "[host:port]"

    def make_server(
            self, server_class, handler_class, authorizer_class, host_port,
            file_access_user=None, **handler_options):
        return utils.make_server(
            server_class, handler_class, authorizer_class, host_port,
            file_access_user=None, **handler_options)

    def handle(self, *args, **options):
        # bind host and port
        if len(args) > 0:
            host_port = args[0]
        else:
            host_port = None
        if host_port:
            host, _port = host_port.split(':', 1)
            port = int(_port)
        else:
            host = utils.get_settings_value('FTPSERVER_HOST') or '127.0.0.1'
            port = utils.get_settings_value('FTPSERVER_PORT') or 21

        timeout = options['timeout'] \
            or utils.get_settings_value('FTPSERVER_TIMEOUT')

        # passive ports
        _passive_ports = options['passive-ports'] \
            or utils.get_settings_value('FTPSERVER_PASSIVE_PORTS')
        if _passive_ports:
            try:
                passive_ports = utils.parse_ports(_passive_ports)
            except (TypeError, ValueError):
                raise CommandError("Invalid passive ports: {}".format(
                    options['passive-ports']))
        else:
            passive_ports = None

        # masquerade address
        masquerade_address = options['masquerade-address'] \
            or utils.get_settings_value('FTPSERVER_MASQUERADE_ADDRESS')

        # file access user
        file_access_user = options['file-access-user'] \
            or utils.get_settings_value('FTPSERVER_FILE_ACCESS_USER')

        # daemonize
        daemonize = options['daemonize'] \
            or utils.get_settings_value('FTPSERVER_DAEMONIZE')
        if daemonize:
            daemonize_options = utils.get_settings_value(
                'FTPSERVER_DAEMONIZE_OPTIONS') or {}
            become_daemon(**daemonize_options)

        # write pid to file
        pidfile = options['pidfile'] \
            or utils.get_settings_value('FTPSERVER_PIDFILE')
        if pidfile:
            with open(pidfile, 'w') as f:
                f.write(str(os.getpid()))

        # setup server
        server = self.make_server(
            server_class=FTPServer,
            handler_class=FTPHandler,
            authorizer_class=FTPAccountAuthorizer,
            host_port=(host, port),
            file_access_user=file_access_user,
            timeout=timeout,
            passive_ports=passive_ports,
            masquerade_address=masquerade_address)

        # start server
        quit_command = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'
        sys.stdout.write((
            "Django version {version_dj}, using settings '{settings}'\n"
            "pyftpdlib version {version_ftp}\n"
            "Quit the server with {quit_command}.\n").format(
            version_dj=get_version(),
            version_ftp=pyftpdlib.__ver__,
            settings=settings.SETTINGS_MODULE,
            quit_command=quit_command))
        server.serve_forever()
