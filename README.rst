=================
Django FTP server
=================

|build-status| |pypi| |python-version| |docs|

FTP server application that used user authentication of Django.

Getting Started
===============

1.  Install django-ftpserver by pip.

::

   $ pip install django-ftpserver

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

* Target Python version is 3.6, 3.7, 3.8, 3.9, 3.10
* Django>=2.2
* pyftpdlib

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
