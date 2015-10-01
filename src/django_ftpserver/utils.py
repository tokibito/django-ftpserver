from django.conf import settings


def get_settings_value(name):
    """Return the django settings value for name attribute
    """
    return getattr(settings, name, None)


def parse_ports(ports_text):
    """Parse ports text

    e.g. ports_text = "12345,13000-15000,20000-30000"
    """
    ports_set = set()
    for bit in ports_text.split(','):
        if '-' in bit:
            low, high = bit.split('-', 1)
            ports_set = ports_set.union(range(int(low), int(high) + 1))
        else:
            ports_set.add(int(bit))
    return sorted(list(ports_set))


def import_class(class_path):
    from importlib import import_module
    pieces = class_path.split('.')
    module = '.'.join(pieces[:-1])
    cls = pieces[-1]
    module = import_module(module)
    return getattr(module, cls)


def make_server(
        server_class, handler_class, authorizer_class, host_port,
        file_access_user=None, **handler_options):
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
    if isinstance(handler_class, basestring):
        handler_class = import_class(handler_class)

    if isinstance(authorizer_class, basestring):
        authorizer_class = import_class(authorizer_class)

    authorizer = authorizer_class(file_access_user)
    handler = handler_class
    for key, value in handler_options.items():
        setattr(handler, key, value)
    handler.authorizer = authorizer
    return server_class(host_port, handler)
