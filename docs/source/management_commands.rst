===================
Management commands
===================

Django FTP server adds several commands to ``manage.py``.

ftpserver
=========

Start the FTP server.

Usage::

   $ python manage.py ftpserver [options] [host:port]

``[host:port]`` is the bind address for the FTP server.
The default is ``127.0.0.1:21``.

.. note::

   Since the default port is 21 (a well-known port), you need root permissions to run the server with default settings.
   To run without root permissions, specify a port above 1023 (e.g., ``python manage.py ftpserver 127.0.0.1:2121``).

For example, this binds to 10.0.0.1:21::

   $ python manage.py ftpserver 10.0.0.1:21

.. csv-table:: options
   :header-rows: 1

   Option,Description
   ``--daemonize``,Run as a background service.
   ``--pidfile=PIDFILE``,File path to write the process ID (PID).
   ``--timeout=TIMEOUT``,Timeout for remote clients (in seconds).
   ``--passive-ports=PASSIVE-PORTS``,"Passive ports (e.g., ``12345,30000-50000``)."
   ``--masquerade-address=MASQUERADE-ADDRESS``,Masquerade address for NAT environments.
   ``--file-access-user=FILE-ACCESS-USER``,System user for file access.
   ``--certfile=CERTFILE``,TLS certificate file.
   ``--keyfile=KEYFILE``,TLS private key file.
   ``--sendfile``,Use sendfile for faster file transfers.

createftpuseraccount
====================

Create an FTP user account (FTPUserAccount record).

Usage::

   $ python manage.py createftpuseraccount <username> <group> [home_dir]

Arguments:

- ``<username>``: The username of an existing Django user.
- ``<group>``: The name of an existing FTP user group.
- ``[home_dir]``: Optional home directory for this user.

createftpusergroup
==================

Create an FTP user group (FTPUserGroup record).

Usage::

   $ python manage.py createftpusergroup <name> [home_dir]

Arguments:

- ``<name>``: The name of the group.
- ``[home_dir]``: Optional home directory for this group.

listftpusergroup
================

List all FTP user groups.

Usage::

   $ python manage.py listftpusergroup

deleteftpusergroup
==================

Delete an FTP user group (FTPUserGroup record).

Usage::

   $ python manage.py deleteftpusergroup <name>

.. note::

   The group must not have any associated user accounts. Delete the user accounts first.

listftpuseraccount
==================

List all FTP user accounts.

Usage::

   $ python manage.py listftpuseraccount

deleteftpuseraccount
====================

Delete an FTP user account (FTPUserAccount record).

Usage::

   $ python manage.py deleteftpuseraccount <username>