========
Overview
========

Origin
======

The origin of this project is `unboxftpd <https://bitbucket.org/tokibito/unboxftpd>`_.

It was refactored from unboxftpd and add some function.

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

3. syncdb app.

::

   $ python manage.py syncdb

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
