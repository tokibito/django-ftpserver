def setup_django():
    from django.conf import settings
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django_ftpserver',
            ),
            MIDDLEWARE_CLASSES=(),
        )
    from django import VERSION as version
    # In Django 1.7 or later, using "django.apps" module.
    if version[0] == 1 and version[1] >= 7:
        from django.apps import apps
        if not apps.ready:
            apps.populate(settings.INSTALLED_APPS)
            from django.core.management import call_command
            call_command('syncdb', interactive=False)
    else:
        from django.db.models.loading import cache as model_cache
        if not model_cache.loaded:
            model_cache._populate()
            from django.core.management import call_command
            call_command('syncdb', interactive=False)
