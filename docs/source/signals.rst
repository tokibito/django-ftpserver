=======
Signals
=======

Django FTP Server provides Django signals that are emitted when various FTP events occur.
This allows you to hook into FTP server events for logging, auditing, or custom processing.

Available Signals
=================

All signals are defined in ``django_ftpserver.signals``.

Connection Signals
------------------

``ftp_server_started``
    Sent when the FTP server starts.

    Arguments:
        - ``sender``: The command class
        - ``server``: The FTPServer instance
        - ``host``: Server host address
        - ``port``: Server port number

``ftp_server_stopped``
    Sent when the FTP server stops.

    Arguments:
        - ``sender``: The command class
        - ``server``: The FTPServer instance
        - ``host``: Server host address
        - ``port``: Server port number

``ftp_client_connected``
    Sent when a client connects to the server.

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``remote_ip``: Client IP address
        - ``remote_port``: Client port number

``ftp_client_disconnected``
    Sent when a client disconnects from the server.

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username (if authenticated, otherwise None)
        - ``remote_ip``: Client IP address

Authentication Signals
----------------------

``ftp_login``
    Sent when a user successfully logs in.

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``remote_ip``: Client IP address

``ftp_login_failed``
    Sent when a login attempt fails.

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Attempted username
        - ``remote_ip``: Client IP address

``ftp_logout``
    Sent when a user logs out.

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``remote_ip``: Client IP address

File Transfer Signals
---------------------

``ftp_file_received``
    Sent when a file upload completes successfully.

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``path``: File path
        - ``remote_ip``: Client IP address

``ftp_file_sent``
    Sent when a file download completes successfully.

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``path``: File path
        - ``remote_ip``: Client IP address

``ftp_file_received_incomplete``
    Sent when a file upload is interrupted.

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``path``: File path
        - ``remote_ip``: Client IP address

``ftp_file_sent_incomplete``
    Sent when a file download is interrupted.

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``path``: File path
        - ``remote_ip``: Client IP address

File Operation Signals
----------------------

``ftp_file_deleted``
    Sent when a file is deleted (DELE command).

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``path``: Deleted file path
        - ``remote_ip``: Client IP address

``ftp_file_renamed``
    Sent when a file or directory is renamed (RNFR/RNTO commands).

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``path_from``: Original path
        - ``path_to``: New path
        - ``remote_ip``: Client IP address

``ftp_directory_created``
    Sent when a directory is created (MKD command).

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``path``: Created directory path
        - ``remote_ip``: Client IP address

``ftp_directory_deleted``
    Sent when a directory is deleted (RMD command).

    Arguments:
        - ``sender``: The handler class
        - ``handler``: The FTPHandler instance
        - ``username``: Username
        - ``path``: Deleted directory path
        - ``remote_ip``: Client IP address

Usage Examples
==============

Basic Signal Receiver
---------------------

Create a file ``receivers.py`` in your Django app::

    import logging
    from django.dispatch import receiver
    from django_ftpserver.signals import ftp_login, ftp_logout, ftp_login_failed

    logger = logging.getLogger('ftp.access')

    @receiver(ftp_login)
    def log_ftp_login(sender, username, remote_ip, **kwargs):
        logger.info("FTP login: user=%s, ip=%s", username, remote_ip)

    @receiver(ftp_logout)
    def log_ftp_logout(sender, username, remote_ip, **kwargs):
        logger.info("FTP logout: user=%s, ip=%s", username, remote_ip)

    @receiver(ftp_login_failed)
    def log_ftp_login_failed(sender, username, remote_ip, **kwargs):
        logger.warning("FTP login failed: user=%s, ip=%s", username, remote_ip)

Make sure to import your receivers in your app's ``apps.py``::

    from django.apps import AppConfig

    class MyAppConfig(AppConfig):
        name = 'myapp'

        def ready(self):
            import myapp.receivers  # noqa

File Upload Processing
----------------------

Process uploaded files (e.g., virus scanning, thumbnail generation)::

    from django.dispatch import receiver
    from django_ftpserver.signals import ftp_file_received

    @receiver(ftp_file_received)
    def process_uploaded_file(sender, username, path, **kwargs):
        # Queue async task for heavy processing
        from myapp.tasks import process_file
        process_file.delay(path, username)

Audit Logging
-------------

Store FTP events in a database for auditing::

    from django.dispatch import receiver
    from django_ftpserver.signals import (
        ftp_login, ftp_logout,
        ftp_file_received, ftp_file_sent, ftp_file_deleted
    )
    from myapp.models import FTPAuditLog

    @receiver(ftp_login)
    def audit_login(sender, username, remote_ip, **kwargs):
        FTPAuditLog.objects.create(
            event_type='login',
            username=username,
            remote_ip=remote_ip,
        )

    @receiver(ftp_file_received)
    def audit_upload(sender, username, path, remote_ip, **kwargs):
        FTPAuditLog.objects.create(
            event_type='upload',
            username=username,
            remote_ip=remote_ip,
            path=path,
        )

    @receiver(ftp_file_deleted)
    def audit_delete(sender, username, path, remote_ip, **kwargs):
        FTPAuditLog.objects.create(
            event_type='delete',
            username=username,
            remote_ip=remote_ip,
            path=path,
        )

Debug Logging
=============

The FTP handlers emit DEBUG level logs for all events. You can enable these
logs in your Django settings::

    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {'class': 'logging.StreamHandler'},
        },
        'loggers': {
            'django_ftpserver.handlers': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }

To disable the debug logs, set the level to INFO or higher::

    LOGGING = {
        'version': 1,
        'loggers': {
            'django_ftpserver.handlers': {
                'level': 'INFO',
            },
        },
    }

Handler Classes
===============

To use signals, make sure you are using the Django FTP handlers. By default,
the management command uses these handlers automatically.

Available handlers:

- ``django_ftpserver.handlers.DjangoFTPHandler`` - FTP handler with signal support
- ``django_ftpserver.handlers.DjangoTLS_FTPHandler`` - TLS FTP handler with signal support (requires pyOpenSSL)

You can also specify custom handlers in your Django settings::

    FTPSERVER_HANDLER = 'django_ftpserver.handlers.DjangoFTPHandler'
    FTPSERVER_TLSHANDLER = 'django_ftpserver.handlers.DjangoTLS_FTPHandler'
