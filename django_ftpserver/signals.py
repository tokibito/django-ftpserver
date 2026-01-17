"""
Django signals for FTP server events.

These signals are emitted by DjangoFTPHandler and DjangoTLS_FTPHandler
when various FTP events occur.
"""

from django.dispatch import Signal


# Connection events
ftp_server_started = Signal()
ftp_server_stopped = Signal()
ftp_client_connected = Signal()
ftp_client_disconnected = Signal()

# Authentication events
ftp_login = Signal()
ftp_login_failed = Signal()
ftp_logout = Signal()

# File transfer events
ftp_file_received = Signal()
ftp_file_sent = Signal()
ftp_file_received_incomplete = Signal()
ftp_file_sent_incomplete = Signal()

# File operation events
ftp_file_deleted = Signal()
ftp_file_renamed = Signal()
ftp_directory_created = Signal()
ftp_directory_deleted = Signal()
