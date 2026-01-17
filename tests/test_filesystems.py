"""Tests for django_ftpserver.filesystems module.

This module tests the StorageFS class and its associated storage patches
that provide compatibility with different Django storage backends.
"""

from unittest import mock
from datetime import datetime

from django.test import TestCase

from django_ftpserver.filesystems import (
    PseudoStat,
    StoragePatch,
    FileSystemStoragePatch,
    S3Boto3StoragePatch,
    DjangoGCloudStoragePatch,
    GoogleCloudStoragePatch,
    StorageFS,
)


class PseudoStatTest(TestCase):
    """Tests for PseudoStat namedtuple."""

    def test_create(self):
        """PseudoStat should store file stat information correctly."""
        stat = PseudoStat(
            st_size=100,
            st_mtime=1234567890,
            st_nlink=1,
            st_mode=0o0100770,
            st_uid=1000,
            st_gid=1000,
            st_dev=0,
            st_ino=0,
        )
        self.assertEqual(stat.st_size, 100)
        self.assertEqual(stat.st_mtime, 1234567890)
        self.assertEqual(stat.st_mode, 0o0100770)


class StoragePatchTest(TestCase):
    """Tests for StoragePatch base class."""

    def test_apply_patches_methods(self):
        """apply() replaces methods and preserves originals with _origin_ prefix."""

        class TestPatch(StoragePatch):
            patch_methods = ("test_method",)

            def test_method(self):
                return "patched"

        class MockFS:
            def test_method(self):
                return "original"

        fs = MockFS()
        TestPatch.apply(fs)

        self.assertEqual(fs._patch, TestPatch)
        self.assertEqual(fs.test_method(), "patched")
        self.assertEqual(fs._origin_test_method(), "original")


class FileSystemStoragePatchTest(TestCase):
    """Tests for FileSystemStoragePatch.

    This patch provides mkdir, rmdir, and stat operations for Django's
    FileSystemStorage by delegating to os module functions.
    """

    def test_patch_methods(self):
        """FileSystemStoragePatch should patch mkdir, rmdir, and stat methods."""
        self.assertEqual(
            FileSystemStoragePatch.patch_methods, ("mkdir", "rmdir", "stat")
        )

    @mock.patch("os.mkdir")
    def test_mkdir(self, mock_mkdir):
        """mkdir() should create directory using storage.path() resolved path."""
        mock_storage = mock.Mock()
        mock_storage.path.return_value = "/full/path/test"

        fs = mock.Mock()
        fs.storage = mock_storage

        FileSystemStoragePatch.mkdir(fs, "test")

        mock_storage.path.assert_called_once_with("test")
        mock_mkdir.assert_called_once_with("/full/path/test")

    @mock.patch("os.rmdir")
    def test_rmdir(self, mock_rmdir):
        """rmdir() should remove directory using storage.path() resolved path."""
        mock_storage = mock.Mock()
        mock_storage.path.return_value = "/full/path/test"

        fs = mock.Mock()
        fs.storage = mock_storage

        FileSystemStoragePatch.rmdir(fs, "test")

        mock_storage.path.assert_called_once_with("test")
        mock_rmdir.assert_called_once_with("/full/path/test")

    @mock.patch("os.stat")
    def test_stat(self, mock_stat):
        """stat() should return os.stat() result for storage.path() resolved path."""
        mock_storage = mock.Mock()
        mock_storage.path.return_value = "/full/path/test"
        mock_stat.return_value = "stat_result"

        fs = mock.Mock()
        fs.storage = mock_storage

        result = FileSystemStoragePatch.stat(fs, "test")

        mock_storage.path.assert_called_once_with("test")
        mock_stat.assert_called_once_with("/full/path/test")
        self.assertEqual(result, "stat_result")


class S3Boto3StoragePatchTest(TestCase):
    """Tests for S3Boto3StoragePatch.

    This patch handles S3-specific behavior where directories are not actual
    S3 objects. It patches _exists, isdir, and getmtime methods.
    """

    def test_patch_methods(self):
        """S3Boto3StoragePatch should patch _exists, isdir, and getmtime methods."""
        self.assertEqual(
            S3Boto3StoragePatch.patch_methods, ("_exists", "isdir", "getmtime")
        )

    def test_exists_directory(self):
        """_exists() returns True for paths ending with / without calling storage."""
        fs = mock.Mock()
        result = S3Boto3StoragePatch._exists(fs, "test/")
        self.assertTrue(result)
        fs.storage.exists.assert_not_called()

    def test_exists_file(self):
        """_exists() should delegate to storage.exists() for file paths."""
        fs = mock.Mock()
        fs.storage.exists.return_value = True

        result = S3Boto3StoragePatch._exists(fs, "test.txt")

        self.assertTrue(result)
        fs.storage.exists.assert_called_once_with("test.txt")

    def test_isdir(self):
        """isdir() should return True if path is not a file."""
        fs = mock.Mock()
        fs.isfile.return_value = False

        result = S3Boto3StoragePatch.isdir(fs, "test/")

        self.assertTrue(result)
        fs.isfile.assert_called_once_with("test/")

    def test_getmtime_directory(self):
        """getmtime() should return 0 for directories (no mtime on S3 prefixes)."""
        fs = mock.Mock()
        fs.isdir.return_value = True

        result = S3Boto3StoragePatch.getmtime(fs, "test/")

        self.assertEqual(result, 0)

    def test_getmtime_file(self):
        """getmtime() should delegate to _origin_getmtime() for files."""
        fs = mock.Mock()
        fs.isdir.return_value = False
        fs._origin_getmtime.return_value = 1234567890

        result = S3Boto3StoragePatch.getmtime(fs, "test.txt")

        self.assertEqual(result, 1234567890)
        fs._origin_getmtime.assert_called_once_with("test.txt")


class DjangoGCloudStoragePatchTest(TestCase):
    """Tests for DjangoGCloudStoragePatch.

    This patch is for django-gcloud-storage library. It includes listdir patch
    that adds trailing slash to paths, which is required by that library.
    """

    def test_patch_methods(self):
        """DjangoGCloudStoragePatch patches _exists, isdir, getmtime, and listdir."""
        self.assertEqual(
            DjangoGCloudStoragePatch.patch_methods,
            ("_exists", "isdir", "getmtime", "listdir"),
        )

    def test_exists_directory(self):
        """_exists() returns True for paths ending with / without calling storage."""
        fs = mock.Mock()
        result = DjangoGCloudStoragePatch._exists(fs, "test/")
        self.assertTrue(result)
        fs.storage.exists.assert_not_called()

    def test_exists_file(self):
        """_exists() should delegate to storage.exists() for file paths."""
        fs = mock.Mock()
        fs.storage.exists.return_value = True

        result = DjangoGCloudStoragePatch._exists(fs, "test.txt")

        self.assertTrue(result)
        fs.storage.exists.assert_called_once_with("test.txt")

    def test_listdir_adds_trailing_slash(self):
        """listdir() should add trailing slash to path if missing."""
        fs = mock.Mock()
        fs._origin_listdir.return_value = (["dir1"], ["file1.txt"])

        DjangoGCloudStoragePatch.listdir(fs, "test")

        fs._origin_listdir.assert_called_once_with("test/")

    def test_listdir_with_trailing_slash(self):
        """listdir() should not add extra slash if path already ends with /."""
        fs = mock.Mock()
        fs._origin_listdir.return_value = (["dir1"], ["file1.txt"])

        DjangoGCloudStoragePatch.listdir(fs, "test/")

        fs._origin_listdir.assert_called_once_with("test/")


class GoogleCloudStoragePatchTest(TestCase):
    """Tests for GoogleCloudStoragePatch.

    This patch is for django-storages GoogleCloudStorage.
    Unlike DjangoGCloudStoragePatch, it does NOT include listdir patch
    because django-storages handles trailing slashes internally.
    """

    def test_patch_methods(self):
        """GoogleCloudStoragePatch does NOT include listdir."""
        self.assertEqual(
            GoogleCloudStoragePatch.patch_methods, ("_exists", "isdir", "getmtime")
        )

    def test_exists_directory(self):
        """_exists() returns True for paths ending with / without calling storage."""
        fs = mock.Mock()
        result = GoogleCloudStoragePatch._exists(fs, "test/")
        self.assertTrue(result)
        fs.storage.exists.assert_not_called()

    def test_exists_file(self):
        """_exists() should delegate to storage.exists() for file paths."""
        fs = mock.Mock()
        fs.storage.exists.return_value = True

        result = GoogleCloudStoragePatch._exists(fs, "test.txt")

        self.assertTrue(result)
        fs.storage.exists.assert_called_once_with("test.txt")

    def test_isdir(self):
        """isdir() should return True if path is not a file."""
        fs = mock.Mock()
        fs.isfile.return_value = False

        result = GoogleCloudStoragePatch.isdir(fs, "test/")

        self.assertTrue(result)

    def test_getmtime_directory(self):
        """getmtime() should return 0 for directories."""
        fs = mock.Mock()
        fs.isdir.return_value = True

        result = GoogleCloudStoragePatch.getmtime(fs, "test/")

        self.assertEqual(result, 0)

    def test_getmtime_file(self):
        """getmtime() should delegate to _origin_getmtime() for files."""
        fs = mock.Mock()
        fs.isdir.return_value = False
        fs._origin_getmtime.return_value = 1234567890

        result = GoogleCloudStoragePatch.getmtime(fs, "test.txt")

        self.assertEqual(result, 1234567890)


class StorageFSTest(TestCase):
    """Tests for StorageFS class.

    StorageFS provides a pyftpdlib-compatible filesystem interface
    that bridges to Django's storage API.
    """

    def _create_fs(self, storage_mock):
        """Helper to create StorageFS instance with mocked storage."""
        with mock.patch(
            "django_ftpserver.filesystems.storages", {"default": storage_mock}
        ):
            cmd_channel = mock.Mock()
            fs = StorageFS("/", cmd_channel)
        return fs

    def test_patches_registry(self):
        """StorageFS should have patches registered for known storage backends."""
        self.assertIn("FileSystemStorage", StorageFS.patches)
        self.assertIn("S3Boto3Storage", StorageFS.patches)
        self.assertIn("S3Storage", StorageFS.patches)
        self.assertIn("DjangoGCloudStorage", StorageFS.patches)
        self.assertIn("GoogleCloudStorage", StorageFS.patches)

    def test_s3_storage_uses_same_patch(self):
        """S3Storage (django-storages 1.14+) should use same patch as S3Boto3Storage."""
        self.assertIs(
            StorageFS.patches["S3Storage"], StorageFS.patches["S3Boto3Storage"]
        )

    def test_gcloud_storages_use_different_patches(self):
        """DjangoGCloudStorage and GoogleCloudStorage should use different patches."""
        self.assertIsNot(
            StorageFS.patches["DjangoGCloudStorage"],
            StorageFS.patches["GoogleCloudStorage"],
        )

    def test_get_storage_default(self):
        """get_storage() should return default storage when storage_class is None."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)

        self.assertEqual(fs.storage, mock_storage)

    def test_listdir(self):
        """listdir() should return directories with trailing / and files without."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"
        mock_storage.listdir.return_value = (
            ["dir1", "dir2"],
            ["file1.txt", "file2.py"],
        )

        fs = self._create_fs(mock_storage)
        result = fs.listdir("/")

        self.assertEqual(result, ["dir1/", "dir2/", "file1.txt", "file2.py"])
        mock_storage.listdir.assert_called_once_with("")

    def test_listdir_filters_empty_names(self):
        """listdir() should filter out empty directory and file names."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"
        mock_storage.listdir.return_value = (["dir1", ""], ["file1.txt", ""])

        fs = self._create_fs(mock_storage)
        result = fs.listdir("/")

        self.assertEqual(result, ["dir1/", "file1.txt"])

    def test_remove(self):
        """remove() should delegate to storage.delete()."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)
        fs.remove("test.txt")

        mock_storage.delete.assert_called_once_with("test.txt")

    def test_isfile(self):
        """isfile() should return True for existing paths not ending with /."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"
        mock_storage.exists.return_value = True

        fs = self._create_fs(mock_storage)

        self.assertTrue(fs.isfile("test.txt"))
        self.assertFalse(fs.isfile("test/"))

    def test_isdir(self):
        """isdir() should return True for empty string or paths ending with /."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"
        mock_storage.exists.return_value = True

        fs = self._create_fs(mock_storage)

        self.assertTrue(fs.isdir(""))
        self.assertTrue(fs.isdir("test/"))

    def test_islink(self):
        """islink() should always return False (no symlinks in storage)."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)

        self.assertFalse(fs.islink("test.txt"))

    def test_getsize_file(self):
        """getsize() should return storage.size() for files."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"
        # exists returns True only for file path, False for directory check
        mock_storage.exists.side_effect = lambda p: p == "test.txt"
        mock_storage.size.return_value = 1024

        fs = self._create_fs(mock_storage)
        result = fs.getsize("test.txt")

        self.assertEqual(result, 1024)

    def test_getsize_directory(self):
        """getsize() should return 0 for directories."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"
        mock_storage.exists.return_value = True

        fs = self._create_fs(mock_storage)
        result = fs.getsize("test/")

        self.assertEqual(result, 0)

    def test_getmtime(self):
        """getmtime() should return timestamp from storage.get_modified_time()."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"
        mock_storage.get_modified_time.return_value = datetime(2025, 1, 1, 12, 0, 0)

        fs = self._create_fs(mock_storage)
        result = fs.getmtime("test.txt")

        self.assertIsInstance(result, float)
        mock_storage.get_modified_time.assert_called_once_with("test.txt")

    def test_stat_file(self):
        """stat() should return PseudoStat with file mode (0o0100770) for files."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"
        # exists returns True only for file path, False for directory check
        mock_storage.exists.side_effect = lambda p: p == "test.txt"
        mock_storage.size.return_value = 1024
        mock_storage.get_modified_time.return_value = datetime(2025, 1, 1, 12, 0, 0)

        fs = self._create_fs(mock_storage)
        result = fs.stat("test.txt")

        self.assertIsInstance(result, PseudoStat)
        self.assertEqual(result.st_size, 1024)
        self.assertEqual(result.st_mode, 0o0100770)

    def test_stat_directory(self):
        """stat() returns PseudoStat with directory mode (0o0040770) for dirs."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"
        mock_storage.exists.return_value = True
        mock_storage.get_modified_time.return_value = datetime(2025, 1, 1, 12, 0, 0)

        fs = self._create_fs(mock_storage)
        result = fs.stat("test/")

        self.assertIsInstance(result, PseudoStat)
        self.assertEqual(result.st_size, 0)
        self.assertEqual(result.st_mode, 0o0040770)

    def test_realpath(self):
        """realpath() should return path unchanged."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)

        self.assertEqual(fs.realpath("/test/path"), "/test/path")

    def test_get_user_by_uid(self):
        """get_user_by_uid() should return 'owner' for any uid."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)

        self.assertEqual(fs.get_user_by_uid(1000), "owner")

    def test_get_group_by_gid(self):
        """get_group_by_gid() should return 'group' for any gid."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)

        self.assertEqual(fs.get_group_by_gid(1000), "group")

    def test_chdir(self):
        """chdir() should update _cwd to the given path."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)
        fs.chdir("/new/path")

        self.assertEqual(fs._cwd, "/new/path")

    def test_mkstemp_not_implemented(self):
        """mkstemp() should raise NotImplementedError."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)

        with self.assertRaises(NotImplementedError):
            fs.mkstemp()

    def test_mkdir_not_implemented(self):
        """mkdir() should raise NotImplementedError (unless patched)."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)

        with self.assertRaises(NotImplementedError):
            fs.mkdir("/test")

    def test_rmdir_not_implemented(self):
        """rmdir() should raise NotImplementedError (unless patched)."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)

        with self.assertRaises(NotImplementedError):
            fs.rmdir("/test")

    def test_chmod_not_implemented(self):
        """chmod() should raise NotImplementedError."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "MockStorage"

        fs = self._create_fs(mock_storage)

        with self.assertRaises(NotImplementedError):
            fs.chmod("/test", 0o755)

    def test_apply_patch_for_known_storage(self):
        """apply_patch() should apply correct patch for known storage backends."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "FileSystemStorage"
        mock_storage.path.return_value = "/full/path"

        fs = self._create_fs(mock_storage)

        self.assertEqual(fs._patch, FileSystemStoragePatch)

    def test_apply_patch_for_unknown_storage(self):
        """apply_patch() should not set _patch for unknown storage backends."""
        mock_storage = mock.Mock()
        mock_storage.__class__.__name__ = "UnknownStorage"

        fs = self._create_fs(mock_storage)

        self.assertFalse(hasattr(fs, "_patch"))
