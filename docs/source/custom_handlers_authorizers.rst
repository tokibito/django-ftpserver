===============================
Custom Handlers and Authorizors
===============================

Django FTP Server lets you specify custom handlers and authorizers via Django settings.

Setting Options::

    FTPSERVER_AUTHORIZER = 'django_ftpserver.authorizers.FTPAccountAuthorizer'
    FTPSERVER_HANDLER = 'pyftpdlib.handlers.FTPHandler'
    FTPSERVER_TLSHANDLER = 'pyftpdlib.handlers.TLS_FTPHandler'

The class definitions and methods can be found at the `pyftdblib's documentation <http://pythonhosted.org/pyftpdlib/>`_.
