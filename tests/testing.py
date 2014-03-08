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
            )
        )
    from django.db.models.loading import cache as model_cache
    if not model_cache.loaded:
        model_cache._populate()
