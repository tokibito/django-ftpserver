==========================================
Using Django storage system (Experimental)
==========================================

.. note::

   This function is experimental. The API may change frequently.

Django FTP Server supports the Django storage API.

With StorageFS, you can change the storage of the FTP server to various things.

Architecture
============

The following diagram shows how FTP client requests flow through the system when using Django Storage backends:

.. mermaid::

   sequenceDiagram
       participant Client as FTP Client
       participant FTPServer as FTP Server<br>(pyftpdlib)
       participant Authorizer as FTPAccountAuthorizer
       participant Django as Django Auth
       participant StorageFS as StorageFS
       participant Storage as Django Storage<br>(S3, GCS, etc.)

       Client->>FTPServer: Connect
       FTPServer->>Authorizer: validate_authentication()
       Authorizer->>Django: authenticate()
       Django-->>Authorizer: User
       Authorizer-->>FTPServer: OK
       FTPServer-->>Client: 230 Login successful

       Client->>FTPServer: LIST
       FTPServer->>StorageFS: listdir()
       StorageFS->>Storage: listdir()
       Storage-->>StorageFS: files
       StorageFS-->>FTPServer: file list
       FTPServer-->>Client: Directory listing

       Client->>FTPServer: RETR file.txt
       FTPServer->>StorageFS: open()
       StorageFS->>Storage: open()
       Storage-->>StorageFS: file object
       StorageFS-->>FTPServer: file data
       FTPServer-->>Client: File contents

Settings
========

Example configuration::

   # Change FTP server filesystem
   FTPSERVER_FILESYSTEM = 'django_ftpserver.filesystems.StorageFS'
   # Using Amazon S3 storage (django-storages)
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   # Config for S3Boto3Storage
   AWS_ACCESS_KEY_ID = '(your access key id)'
   AWS_SECRET_ACCESS_KEY = 'your secret access key'
   AWS_STORAGE_BUCKET_NAME = 'your.storage.bucket'
