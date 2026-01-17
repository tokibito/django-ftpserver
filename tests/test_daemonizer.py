"""Tests for django_ftpserver.daemonizer module."""

from unittest import mock

import pytest


class TestNullDevice:
    """Tests for NullDevice class."""

    def _getTargetClass(self):
        from django_ftpserver.daemonizer import NullDevice
        return NullDevice

    def _makeOne(self):
        return self._getTargetClass()()

    def test_write_returns_none(self):
        """write() should return None."""
        device = self._makeOne()
        result = device.write("test data")
        assert result is None

    def test_write_accepts_any_string(self):
        """write() should accept any string without error."""
        device = self._makeOne()
        device.write("")
        device.write("hello")
        device.write("multi\nline\ntext")

    def test_flush_returns_none(self):
        """flush() should return None and not raise any error."""
        device = self._makeOne()
        result = device.flush()
        assert result is None


class TestGetDaemonizeClass:
    """Tests for get_daemonize_class function."""

    def _callFUT(self):
        from django_ftpserver.daemonizer import get_daemonize_class
        return get_daemonize_class()

    def test_returns_posix_class_on_posix(self):
        """Should return PosixDaemonize when os.name is 'posix'."""
        from django_ftpserver.daemonizer import PosixDaemonize

        with mock.patch("django_ftpserver.daemonizer.os.name", "posix"):
            result = self._callFUT()
        assert result is PosixDaemonize

    def test_returns_non_posix_class_on_windows(self):
        """Should return NonPosixDaemonize when os.name is 'nt'."""
        from django_ftpserver.daemonizer import NonPosixDaemonize

        with mock.patch("django_ftpserver.daemonizer.os.name", "nt"):
            result = self._callFUT()
        assert result is NonPosixDaemonize

    def test_returns_non_posix_class_on_other(self):
        """Should return NonPosixDaemonize for any non-posix os.name."""
        from django_ftpserver.daemonizer import NonPosixDaemonize

        with mock.patch("django_ftpserver.daemonizer.os.name", "java"):
            result = self._callFUT()
        assert result is NonPosixDaemonize


class TestBaseDaemonizeInternalMethods:
    """Tests for BaseDaemonize internal methods via concrete classes."""

    def _getTargetClass(self):
        from django_ftpserver.daemonizer import NonPosixDaemonize
        return NonPosixDaemonize

    def _makeOne(self, **kwargs):
        return self._getTargetClass()(**kwargs)

    def test_change_directory(self):
        """_change_directory() should call os.chdir with home_dir."""
        instance = self._makeOne(home_dir="/test/path")

        with mock.patch("django_ftpserver.daemonizer.os.chdir") as mock_chdir:
            instance._change_directory()

        mock_chdir.assert_called_once_with("/test/path")

    def test_change_directory_default(self):
        """_change_directory() should use default home_dir '.'."""
        instance = self._makeOne()

        with mock.patch("django_ftpserver.daemonizer.os.chdir") as mock_chdir:
            instance._change_directory()

        mock_chdir.assert_called_once_with(".")

    def test_set_umask(self):
        """_set_umask() should call os.umask with umask value."""
        instance = self._makeOne(umask=0o077)

        with mock.patch("django_ftpserver.daemonizer.os.umask") as mock_umask:
            instance._set_umask()

        mock_umask.assert_called_once_with(0o077)

    def test_set_umask_default(self):
        """_set_umask() should use default umask 0o022."""
        instance = self._makeOne()

        with mock.patch("django_ftpserver.daemonizer.os.umask") as mock_umask:
            instance._set_umask()

        mock_umask.assert_called_once_with(0o022)


class TestNonPosixDaemonize:
    """Tests for NonPosixDaemonize class."""

    def _getTargetClass(self):
        from django_ftpserver.daemonizer import NonPosixDaemonize
        return NonPosixDaemonize

    def _makeOne(self, **kwargs):
        return self._getTargetClass()(**kwargs)

    def test_daemonize_calls_internal_methods(self):
        """daemonize() should call all internal methods in order."""
        instance = self._makeOne()

        with mock.patch.object(instance, "_change_directory") as mock_cd, \
             mock.patch.object(instance, "_set_umask") as mock_umask, \
             mock.patch.object(instance, "_redirect_streams") as mock_redirect:
            instance.daemonize()

        mock_cd.assert_called_once()
        mock_umask.assert_called_once()
        mock_redirect.assert_called_once()

    def test_redirect_streams_without_logs(self):
        """_redirect_streams() should use NullDevice when logs not specified."""
        from django_ftpserver.daemonizer import NullDevice
        import sys

        instance = self._makeOne()
        mock_stdin = mock.MagicMock()
        mock_stdout = mock.MagicMock()
        mock_stderr = mock.MagicMock()

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        with mock.patch("sys.stdin", mock_stdin), \
             mock.patch("sys.stdout", mock_stdout), \
             mock.patch("sys.stderr", mock_stderr):
            instance._redirect_streams()
            # Check inside the context that NullDevice was assigned
            assert isinstance(sys.stdout, NullDevice)
            assert isinstance(sys.stderr, NullDevice)

        mock_stdin.close.assert_called_once()
        mock_stdout.close.assert_called_once()
        mock_stderr.close.assert_called_once()

        # Restore original streams for subsequent tests
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    def test_redirect_streams_with_out_log(self):
        """_redirect_streams() should open file for out_log."""
        instance = self._makeOne(out_log="/tmp/out.log")
        mock_stdin = mock.MagicMock()
        mock_stdout = mock.MagicMock()
        mock_stderr = mock.MagicMock()
        mock_file = mock.MagicMock()

        with mock.patch("sys.stdin", mock_stdin), \
             mock.patch("sys.stdout", mock_stdout), \
             mock.patch("sys.stderr", mock_stderr), \
             mock.patch("builtins.open", return_value=mock_file) as mock_open:
            instance._redirect_streams()

        mock_open.assert_called_once_with("/tmp/out.log", "a", 1)

    def test_redirect_streams_with_err_log(self):
        """_redirect_streams() should open file for err_log."""
        instance = self._makeOne(err_log="/tmp/err.log")
        mock_stdin = mock.MagicMock()
        mock_stdout = mock.MagicMock()
        mock_stderr = mock.MagicMock()
        mock_file = mock.MagicMock()

        with mock.patch("sys.stdin", mock_stdin), \
             mock.patch("sys.stdout", mock_stdout), \
             mock.patch("sys.stderr", mock_stderr), \
             mock.patch("builtins.open", return_value=mock_file) as mock_open:
            instance._redirect_streams()

        mock_open.assert_called_once_with("/tmp/err.log", "a", 1)

    def test_redirect_streams_with_both_logs(self):
        """_redirect_streams() should open both log files."""
        instance = self._makeOne(out_log="/tmp/out.log", err_log="/tmp/err.log")
        mock_stdin = mock.MagicMock()
        mock_stdout = mock.MagicMock()
        mock_stderr = mock.MagicMock()
        mock_file = mock.MagicMock()

        with mock.patch("sys.stdin", mock_stdin), \
             mock.patch("sys.stdout", mock_stdout), \
             mock.patch("sys.stderr", mock_stderr), \
             mock.patch("builtins.open", return_value=mock_file) as mock_open:
            instance._redirect_streams()

        assert mock_open.call_count == 2
        mock_open.assert_any_call("/tmp/err.log", "a", 1)
        mock_open.assert_any_call("/tmp/out.log", "a", 1)


class TestPosixDaemonize:
    """Tests for PosixDaemonize class."""

    def _getTargetClass(self):
        from django_ftpserver.daemonizer import PosixDaemonize
        return PosixDaemonize

    def _makeOne(self, **kwargs):
        return self._getTargetClass()(**kwargs)

    def test_daemonize_calls_methods_in_order(self):
        """daemonize() should call internal methods in correct order."""
        instance = self._makeOne()

        with mock.patch.object(instance, "_first_fork") as mock_first, \
             mock.patch.object(instance, "_setup_session") as mock_setup, \
             mock.patch.object(instance, "_second_fork") as mock_second, \
             mock.patch.object(instance, "_redirect_streams") as mock_redirect:
            instance.daemonize()

        mock_first.assert_called_once()
        mock_setup.assert_called_once()
        mock_second.assert_called_once()
        mock_redirect.assert_called_once()

    def test_first_fork_child_process(self):
        """_first_fork() in child process (fork returns 0) should continue."""
        instance = self._makeOne()

        with mock.patch("django_ftpserver.daemonizer.os.fork", return_value=0):
            # Should not raise, should continue execution
            instance._first_fork()

    def test_first_fork_parent_process(self):
        """_first_fork() in parent process (fork > 0) should call sys.exit(0)."""
        instance = self._makeOne()

        with mock.patch("django_ftpserver.daemonizer.os.fork", return_value=123), \
             mock.patch("sys.exit") as mock_exit:
            instance._first_fork()

        mock_exit.assert_called_once_with(0)

    def test_first_fork_failure(self):
        """_first_fork() should exit with 1 on OSError."""
        instance = self._makeOne()
        mock_stderr = mock.MagicMock()

        with mock.patch("django_ftpserver.daemonizer.os.fork",
                        side_effect=OSError(1, "fork failed")), \
             mock.patch("sys.stderr", mock_stderr), \
             mock.patch("sys.exit") as mock_exit:
            instance._first_fork()

        mock_stderr.write.assert_called()
        mock_exit.assert_called_once_with(1)

    def test_setup_session(self):
        """_setup_session() should call setsid and internal methods."""
        instance = self._makeOne(home_dir="/test", umask=0o077)

        with mock.patch("django_ftpserver.daemonizer.os.setsid") as mock_setsid, \
             mock.patch("django_ftpserver.daemonizer.os.chdir") as mock_chdir, \
             mock.patch("django_ftpserver.daemonizer.os.umask") as mock_umask:
            instance._setup_session()

        mock_setsid.assert_called_once()
        mock_chdir.assert_called_once_with("/test")
        mock_umask.assert_called_once_with(0o077)

    def test_second_fork_child_process(self):
        """_second_fork() in child process (fork returns 0) should continue."""
        instance = self._makeOne()

        with mock.patch("django_ftpserver.daemonizer.os.fork", return_value=0):
            # Should not raise, should continue execution
            instance._second_fork()

    def test_second_fork_parent_process(self):
        """_second_fork() in parent (fork > 0) should call os._exit(0)."""
        instance = self._makeOne()

        with mock.patch("django_ftpserver.daemonizer.os.fork", return_value=456), \
             mock.patch("os._exit") as mock_exit:
            instance._second_fork()

        mock_exit.assert_called_once_with(0)

    def test_second_fork_failure(self):
        """_second_fork() should exit with 1 on OSError."""
        instance = self._makeOne()
        mock_stderr = mock.MagicMock()

        with mock.patch("django_ftpserver.daemonizer.os.fork",
                        side_effect=OSError(2, "fork failed")), \
             mock.patch("sys.stderr", mock_stderr), \
             mock.patch("os._exit") as mock_exit:
            instance._second_fork()

        mock_stderr.write.assert_called()
        mock_exit.assert_called_once_with(1)

    def test_redirect_streams(self):
        """_redirect_streams() should redirect stdin/stdout/stderr."""
        instance = self._makeOne()
        mock_file = mock.MagicMock()
        mock_file.fileno.return_value = 10

        with mock.patch("builtins.open", return_value=mock_file) as mock_open, \
             mock.patch("django_ftpserver.daemonizer.os.dup2") as mock_dup2, \
             mock.patch("sys.stdin") as mock_stdin, \
             mock.patch("sys.stdout") as mock_stdout, \
             mock.patch("sys.stderr") as mock_stderr:
            mock_stdin.fileno.return_value = 0
            mock_stdout.fileno.return_value = 1
            mock_stderr.fileno.return_value = 2

            instance._redirect_streams()

        # Should open /dev/null for stdin, and /dev/null for out/err by default
        assert mock_open.call_count == 3
        mock_open.assert_any_call("/dev/null", "r")
        mock_open.assert_any_call("/dev/null", "a+", 1)

        # Should call dup2 for stdin, stdout, stderr
        assert mock_dup2.call_count == 3

    def test_redirect_streams_with_logs(self):
        """_redirect_streams() should use log files when specified."""
        instance = self._makeOne(out_log="/var/log/out.log",
                                  err_log="/var/log/err.log")
        mock_file = mock.MagicMock()
        mock_file.fileno.return_value = 10

        with mock.patch("builtins.open", return_value=mock_file) as mock_open, \
             mock.patch("django_ftpserver.daemonizer.os.dup2"), \
             mock.patch("sys.stdin") as mock_stdin, \
             mock.patch("sys.stdout") as mock_stdout, \
             mock.patch("sys.stderr") as mock_stderr:
            mock_stdin.fileno.return_value = 0
            mock_stdout.fileno.return_value = 1
            mock_stderr.fileno.return_value = 2

            instance._redirect_streams()

        mock_open.assert_any_call("/dev/null", "r")
        mock_open.assert_any_call("/var/log/out.log", "a+", 1)
        mock_open.assert_any_call("/var/log/err.log", "a+", 1)


class TestBecomeDaemon:
    """Tests for become_daemon function."""

    def _callFUT(self, **kwargs):
        from django_ftpserver.daemonizer import become_daemon
        return become_daemon(**kwargs)

    def test_become_daemon_uses_correct_class(self):
        """become_daemon() should use class from get_daemonize_class()."""
        mock_daemon_instance = mock.MagicMock()
        mock_daemon_class = mock.MagicMock(return_value=mock_daemon_instance)

        with mock.patch("django_ftpserver.daemonizer.get_daemonize_class",
                        return_value=mock_daemon_class):
            self._callFUT()

        mock_daemon_class.assert_called_once()
        mock_daemon_instance.daemonize.assert_called_once()

    def test_become_daemon_passes_arguments(self):
        """become_daemon() should pass all arguments to the daemon class."""
        mock_daemon_instance = mock.MagicMock()
        mock_daemon_class = mock.MagicMock(return_value=mock_daemon_instance)

        with mock.patch("django_ftpserver.daemonizer.get_daemonize_class",
                        return_value=mock_daemon_class):
            self._callFUT(
                our_home_dir="/home/test",
                out_log="/var/log/out.log",
                err_log="/var/log/err.log",
                umask=0o077
            )

        mock_daemon_class.assert_called_once_with(
            home_dir="/home/test",
            out_log="/var/log/out.log",
            err_log="/var/log/err.log",
            umask=0o077
        )

    def test_become_daemon_default_arguments(self):
        """become_daemon() should use default arguments."""
        mock_daemon_instance = mock.MagicMock()
        mock_daemon_class = mock.MagicMock(return_value=mock_daemon_instance)

        with mock.patch("django_ftpserver.daemonizer.get_daemonize_class",
                        return_value=mock_daemon_class):
            self._callFUT()

        mock_daemon_class.assert_called_once_with(
            home_dir=".",
            out_log=None,
            err_log=None,
            umask=0o022
        )
