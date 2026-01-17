from django.conf import settings

# Default values for FTPSERVER_* settings
# Class values are specified as strings to avoid circular imports
FTPSERVER_DEFAULTS = {
    "FTPSERVER_HOST": "127.0.0.1",
    "FTPSERVER_PORT": 21,
    "FTPSERVER_TIMEOUT": None,
    "FTPSERVER_PASSIVE_PORTS": None,
    "FTPSERVER_MASQUERADE_ADDRESS": None,
    "FTPSERVER_FILE_ACCESS_USER": None,
    "FTPSERVER_CERTFILE": None,
    "FTPSERVER_KEYFILE": None,
    "FTPSERVER_SENDFILE": None,
    "FTPSERVER_DAEMONIZE": False,
    "FTPSERVER_DAEMONIZE_OPTIONS": {},
    "FTPSERVER_PIDFILE": None,
    "FTPSERVER_HANDLER": "django_ftpserver.handlers.DjangoFTPHandler",
    "FTPSERVER_TLSHANDLER": "django_ftpserver.handlers.DjangoTLS_FTPHandler",
    "FTPSERVER_AUTHORIZER": "django_ftpserver.authorizers.FTPAccountAuthorizer",
    "FTPSERVER_FILESYSTEM": None,
}


def get_settings_value(name):
    """Return the django settings value for name attribute

    .. deprecated::
        Use :func:`get_ftp_setting` instead.
    """
    import warnings

    warnings.warn(
        "get_settings_value is deprecated, use get_ftp_setting instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(settings, name, None)


def get_ftp_setting(name):
    """Return the FTP server setting value with default fallback.

    First checks Django settings, then falls back to FTPSERVER_DEFAULTS.
    """
    value = getattr(settings, name, None)
    if value is None:
        return FTPSERVER_DEFAULTS.get(name)
    return value


def parse_ports(ports_text):
    """Parse ports text

    e.g. ports_text = "12345,13000-15000,20000-30000"
    """
    ports_set = set()
    for bit in ports_text.split(","):
        if "-" in bit:
            low, high = bit.split("-", 1)
            ports_set = ports_set.union(range(int(low), int(high) + 1))
        else:
            ports_set.add(int(bit))
    return sorted(list(ports_set))


def import_class(class_path):
    from importlib import import_module

    pieces = class_path.split(".")
    module = ".".join(pieces[:-1])
    cls = pieces[-1]
    module = import_module(module)
    return getattr(module, cls)


def make_server(
    server_class,
    handler_class,
    authorizer_class,
    filesystem_class,
    host_port,
    file_access_user=None,
    **handler_options,
):
    """make server instance

    :host_port: (host, port)
    :file_access_user: 'spam'

    handler_options:

      * timeout
      * passive_ports
      * masquerade_address
      * certfile
      * keyfile
    """
    if isinstance(handler_class, str):
        handler_class = import_class(handler_class)

    if isinstance(authorizer_class, str):
        authorizer_class = import_class(authorizer_class)

    if isinstance(filesystem_class, str):
        filesystem_class = import_class(filesystem_class)

    authorizer = authorizer_class(file_access_user)
    handler = handler_class
    for key, value in handler_options.items():
        setattr(handler, key, value)
    handler.authorizer = authorizer
    if filesystem_class is not None:
        handler.abstracted_fs = filesystem_class
    return server_class(host_port, handler)
