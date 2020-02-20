==============
Change History
==============

0.7.0
=====
:release-date: 2020-02-20

* Added Django 3.0 support
* Added Python 3.8 support
* Removed Django <2.0 support
* Removed Python 2.7 support
* Removed six dependency

0.6.0
=====
:release-date: 2018-11-26

* Added Django 2.0, 2.1 support
* Removed Django <1.11 support
* Change the test runner from nose to pytest

0.5.0
=====
:release-date: 2017-05-24

* Added storage system support `#14`_
* Added Django 1.11 support

.. _#14: https://github.com/tokibito/django-ftpserver/pull/14

0.4.1
=====
:release-date: 2017-03-27

* Update daemonize.py `#13`_
* Add six module to install_require
* Added Python 3.6 support

.. _#13: https://github.com/tokibito/django-ftpserver/pull/13

0.4.0
=====
:release-date: 2016-09-16

* WIP: Added django 1.10 support `#12`_
* Removed older Python(2.6, 3.3) and Django(<1.8) support

.. _#12: https://github.com/tokibito/django-ftpserver/pull/12

0.3.5
=====
:release-date: 2016-01-26

* Fix daemonize problem in Django 1.9 `#10`_

.. _#10: https://github.com/tokibito/django-ftpserver/issues/10

0.3.4
=====
:release-date: 2015-12-15

* add tox env for Django 1.9 and Python 3.5

0.3.3
=====
:release-date: 2015-10-14

* #9 Fix for python3 in utils

0.3.2
=====
:release-date: 2015-10-02

* #7 support Custom Authorizer and Handler classes via settings

0.3.1
=====
:release-date: 2015-03-29

* small refactoring

0.3
===
:release-date: 2015-2-12

* support sendfile (--sendfile option)
* fixes #5 support custom User username field
* fixes #4 support Windows platform
* fixes #1 model string format

0.2
===
:release-date: 2014-03-26

* support TLS (--certfile option)
* testing on Python 3.4

0.1
===
:release-date: 2014-03-09

first release.
