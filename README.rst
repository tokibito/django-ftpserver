=================
Django FTP server
=================

|build-status| |pypi| |python-version| |docs|

FTP server application that used user authentication of Django.

Features
========

* FTP server integrated with Django's user authentication system
* Permission management through FTP user groups (read, write, delete, etc.)
* Per-user and per-group home directory configuration
* FTP account management via Django Admin
* Secure communication with TLS/SSL support (FTPS)
* Daemon mode for background service operation
* Integration with Django Storage backends (S3, Google Cloud Storage, etc.) [#experimental]_
* Passive mode and masquerade address configuration
* Cross-platform support (Windows/Unix)
* Easy setup with management commands (createftpusergroup, createftpuseraccount)

.. [#experimental] Experimental feature. May be removed in future versions.

Getting Started
===============

1.  Install django-ftpserver by pip.

::

   $ pip install django-ftpserver

Optional dependencies can be installed with extras:

::

   # For TLS/SSL support (FTPS)
   $ pip install django-ftpserver[tls]

   # For Windows service support
   $ pip install django-ftpserver[windows]

   # Multiple extras
   $ pip install django-ftpserver[tls,windows]

2. Add line to settings.INSTALLED_APPS for your django project.

::

   INSTALLED_APPS = (
       # ..
       'django_ftpserver',
   )

3. Migrate app.

::

   $ python manage.py migrate

4. Create FTP user group.

::

   $ python manage.py createftpusergroup my-ftp-group

5. Create FTP user account.

::

   $ python manage.py createftpuseraccount <username> my-ftp-group

``<username>`` is the django authentication username.

6. Run ``manage.py ftpserver`` command.

::

   $ python manage.py ftpserver 127.0.0.1:10021

7. Connect with your favorite FTP client.

Requirements
============

* Target Python version is 3.10, 3.11, 3.12, 3.13, 3.14
* Django>=4.2
* pyftpdlib

Optional Dependencies
---------------------

* pyOpenSSL - Required for TLS/SSL support (``pip install django-ftpserver[tls]``)
* pywin32 - Required for Windows service support (``pip install django-ftpserver[windows]``)

License
=======

This software is licensed under the MIT License.

Documentation
=============

The latest documentation is hosted at Read The Docs.

https://django-ftpserver.readthedocs.org/en/latest/

Develop
=======

This project is hosted at Github: https://github.com/tokibito/django-ftpserver

Author
======

* Shinya Okano

.. |build-status| image:: https://github.com/tokibito/django-ftpserver/workflows/Tests/badge.svg
   :target: https://github.com/tokibito/django-ftpserver/actions/workflows/tests.yml
.. |docs| image:: https://readthedocs.org/projects/django-ftpserver/badge/?version=latest
   :target: https://readthedocs.org/projects/django-ftpserver/
.. |pypi| image:: https://badge.fury.io/py/django-ftpserver.svg
   :target: http://badge.fury.io/py/django-ftpserver
.. |python-version| image:: https://img.shields.io/pypi/pyversions/django-ftpserver.svg
   :target: https://pypi.python.org/pypi/django-ftpserver
