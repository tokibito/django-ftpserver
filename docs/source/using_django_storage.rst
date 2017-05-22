==========================================
Using Django storage system (Experimental)
==========================================

.. note::

   This function is experimental. The API may change frequently.

Django FTP Server supports the Django storage API.

With StorageFS, you can change the storage of the FTP server to various things.

Settings::

   # Change FTP server filesystem
   FTPSERVER_FILESYSTEM = 'django_ftpserver.filesystems.StorageFS'
   # Using Amazon S3 storage (django-storages)
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   # Config for S3Boto3Storage
   AWS_ACCESS_KEY_ID = '(your access key id)'
   AWS_SECRET_ACCESS_KEY = 'your secret access key'
   AWS_STORAGE_BUCKET_NAME = 'your.storage.bucket'
