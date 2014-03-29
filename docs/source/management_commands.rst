===================
Management commands
===================

Django FTP server add some commands to ``manage.py`` commands.

ftpserver
=========

Start FTP server.

Usage::

   $ python manage.py ftpserver [options] [host:port]

``[host:port]`` is bind address for FTP server.

For example, it binds to address of 10.0.0.1:21::

   $ python manage.py ftpserver 10.0.0.1:21

.. csv-table:: options
   :header-rows: 1

   Option,Description
   ``--daemonize``,become background service.
   ``--pidfile=PIDFILE``,filename to write process id (PID).
   ``--timeout=TIMEOUT``,timeout for remote client.
   ``--passive-ports=PASSIVE-PORTS``,"Passive ports. eg. 12345,30000-50000"
   ``--masquerade-address=MASQUERADE-ADDRESS``,masquerade address.
   ``--file-access-user=FILE-ACCESS-USER``,user for access to file.
   ``--certfile=CERTFILE``,TLS certificate file.
   ``--keyfile=KEYFILE``,TLS private key file.
   ``--sendfile``,Use sendfile.

createftpuseraccount
====================

Create a FTP user account (FTPUserAccount record).

Usage::

   $ python manage.py createftpuseraccount [options] <username> <group> [home_dir]

createftpusergroup
==================

Create a FTP user group (FTPUserGroup record).

Usage::

   $ python manage.py createftpusergroup [options] <name> [home_dir]
