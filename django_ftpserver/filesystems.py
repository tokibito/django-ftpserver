import logging
import time
import os
from collections import namedtuple

from pyftpdlib.filesystems import AbstractedFS

from django.core.files.storage import (
    get_storage_class as _get_storage_class
)

logger = logging.getLogger(__name__)

PseudoStat = namedtuple(
    'PseudoStat',
    [
        'st_size', 'st_mtime', 'st_nlink', 'st_mode', 'st_uid', 'st_gid',
        'st_dev', 'st_ino'
    ])


class StoragePatch:
    """Base class for patches to StorageFS.
    """
    patch_methods = ()

    @classmethod
    def apply(cls, fs):
        """replace bound methods of fs.
        """
        logger.debug(
            'Patching %s with %s.', fs.__class__.__name__, cls.__name__)
        fs._patch = cls
        for method_name in cls.patch_methods:
            # if fs hasn't method, raise AttributeError.
            origin = getattr(fs, method_name)
            method = getattr(cls, method_name)
            bound_method = method.__get__(fs, fs.__class__)
            setattr(fs, method_name, bound_method)
            setattr(fs, '_origin_' + method_name, origin)


class FileSystemStoragePatch(StoragePatch):
    """StoragePatch for Django's FileSystemStorage.
    """
    patch_methods = (
        'mkdir', 'rmdir', 'stat',
    )

    def mkdir(self, path):
        os.mkdir(self.storage.path(path))

    def rmdir(self, path):
        os.rmdir(self.storage.path(path))

    def stat(self, path):
        return os.stat(self.storage.path(path))


class S3Boto3StoragePatch(StoragePatch):
    """StoragePatch for S3Boto3Storage(provided by django-storages).
    """
    patch_methods = (
        '_exists', 'isdir', 'getmtime',
    )

    def _exists(self, path):
        """S3 directory is not S3Ojbect.
        """
        if path.endswith('/'):
            return True
        return self.storage.exists(path)

    def isdir(self, path):
        return not self.isfile(path)

    def getmtime(self, path):
        if self.isdir(path):
            return 0
        return self._origin_getmtime(path)


class DjangoGCloudStoragePatch(StoragePatch):
    """StoragePatch for DjangoGCloudStorage(provided by django-gcloud-storage).
    """
    patch_methods = (
        '_exists', 'isdir', 'getmtime', 'listdir',
    )

    def _exists(self, path):
        """GCS directory is not blob.
        """
        if path.endswith('/'):
            return True
        return self.storage.exists(path)

    def isdir(self, path):
        return not self.isfile(path)

    def getmtime(self, path):
        if self.isdir(path):
            return 0
        return self._origin_getmtime(path)

    def listdir(self, path):
        if not path.endswith('/'):
            path += '/'
        return self._origin_listdir(path)


class StorageFS(AbstractedFS):
    """FileSystem for bridge to Django storage.
    """
    storage_class = None
    patches = {
        'FileSystemStorage': FileSystemStoragePatch,
        'S3Boto3Storage': S3Boto3StoragePatch,
        'DjangoGCloudStorage': DjangoGCloudStoragePatch,
    }

    def apply_patch(self):
        """apply adjustment patch for storage
        """
        patch = self.patches.get(self.storage.__class__.__name__)
        if patch:
            patch.apply(self)

    def __init__(self, root, cmd_channel):
        super(StorageFS, self).__init__(root, cmd_channel)
        self.storage = self.get_storage()
        self.apply_patch()

    def get_storage_class(self):
        if self.storage_class is None:
            return _get_storage_class()
        return self.storage_class

    def get_storage(self):
        storage_class = self.get_storage_class()
        return storage_class()

    def open(self, filename, mode):
        path = os.path.join(self._cwd, filename)
        return self.storage.open(path, mode)

    def mkstemp(self, suffix='', prefix='', dir=None, mode='wb'):
        raise NotImplementedError

    def chdir(self, path):
        assert isinstance(path, str), path
        self._cwd = self.fs2ftp(path)

    def mkdir(self, path):
        raise NotImplementedError

    def listdir(self, path):
        assert isinstance(path, str), path
        if path == '/':
            path = ''
        directories, files = self.storage.listdir(path)
        return ([name + '/' for name in directories if name]
                + [name for name in files if name])

    def rmdir(self, path):
        raise NotImplementedError

    def remove(self, path):
        assert isinstance(path, str), path
        self.storage.delete(path)

    def chmod(self, path, mode):
        raise NotImplementedError

    def stat(self, path):
        if self.isfile(path):
            st_mode = 0o0100770
        else:
            # directory
            st_mode = 0o0040770
        return PseudoStat(
            st_size=self.getsize(path),
            st_mtime=int(self.getmtime(path)),
            st_nlink=1,
            st_mode=st_mode,
            st_uid=1000,
            st_gid=1000,
            st_dev=0,
            st_ino=0,
        )

    lstat = stat

    def _exists(self, path):
        if path == '/':
            return self.storage.exists("")
        return self.storage.exists(path)

    def isfile(self, path):
        return self._exists(path) and not path.endswith('/')

    def islink(self, path):
        return False

    def isdir(self, path):
        if path == '':
            return True
        elif path.endswith('/'):
            return self._exists(path)
        return self._exists(path + '/')

    def getsize(self, path):
        if self.isdir(path):
            return 0
        return self.storage.size(path)

    def getmtime(self, path):
        return time.mktime(self.storage.get_modified_time(path).timetuple())

    def realpath(self, path):
        return path

    def lexists(self, path):
        return self._exists(path)

    def get_user_by_uid(self, uid):
        return "owner"

    def get_group_by_gid(self, gid):
        return "group"
