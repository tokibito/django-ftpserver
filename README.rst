=================
Django FTP server
=================

|build-status| |pypi| |docs|

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

3. migrate or syncdb(Django<1.7) app.

::

   $ python manage.py migrate

4. Run ``manage.py ftpserver`` command.

::

   $ python manage.py ftpserver 127.0.0.1:10021

Requirements
============

* Target Python version is 2.6, 2.7, 3.3, 3.4.
* Django>=1.4
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

.. |build-status| image:: https://travis-ci.org/tokibito/django-ftpserver.svg?branch=master
   :target: https://travis-ci.org/tokibito/django-ftpserver
.. |docs| image:: https://readthedocs.org/projects/django-ftpserver/badge/?version=latest
   :target: https://readthedocs.org/projects/django-ftpserver/
.. |pypi| image:: https://badge.fury.io/py/django-ftpserver.svg
   :target: http://badge.fury.io/py/django-ftpserver
