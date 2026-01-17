"""Daemon process utilities for POSIX and non-POSIX systems."""

import os
import sys
from abc import ABC, abstractmethod


class BaseDaemonize(ABC):
    """Abstract base class for daemonization."""

    def __init__(
        self,
        home_dir=".",
        out_log=None,
        err_log=None,
        umask=0o022,
    ):
        self.home_dir = home_dir
        self.out_log = out_log
        self.err_log = err_log
        self.umask = umask

    @abstractmethod
    def daemonize(self):
        """Execute the daemonization process."""
        pass

    def _change_directory(self):
        """Change to the home directory."""
        os.chdir(self.home_dir)

    def _set_umask(self):
        """Set the file creation mask."""
        os.umask(self.umask)


class PosixDaemonize(BaseDaemonize):
    """POSIX-compliant daemonization using double-fork."""

    # Line buffering for text I/O
    BUFFERING = 1

    def daemonize(self):
        """Robustly turn into a UNIX daemon."""
        self._first_fork()
        self._setup_session()
        self._second_fork()
        self._redirect_streams()

    def _first_fork(self):
        """First fork to detach from parent."""
        try:
            if os.fork() > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"fork #1 failed: ({e.errno}) {e.strerror}\n")
            sys.exit(1)

    def _setup_session(self):
        """Create new session and change directory."""
        os.setsid()
        self._change_directory()
        self._set_umask()

    def _second_fork(self):
        """Second fork to prevent zombie processes."""
        try:
            if os.fork() > 0:
                os._exit(0)
        except OSError as e:
            sys.stderr.write(f"fork #2 failed: ({e.errno}) {e.strerror}\n")
            os._exit(1)

    def _redirect_streams(self):
        """Redirect stdin, stdout, and stderr."""
        out_log = self.out_log or "/dev/null"
        err_log = self.err_log or "/dev/null"

        si = open("/dev/null", "r")
        so = open(out_log, "a+", self.BUFFERING)
        se = open(err_log, "a+", self.BUFFERING)

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        sys.stdout = so
        sys.stderr = se


class NullDevice:
    """A writable object that writes to nowhere, like /dev/null."""

    def write(self, _s):
        pass

    def flush(self):
        pass


class NonPosixDaemonize(BaseDaemonize):
    """Non-POSIX daemonization simulator using I/O redirection."""

    # Line buffering for text I/O
    BUFFERING = 1

    def daemonize(self):
        """Simulate daemon mode by redirecting I/O and changing directory."""
        self._change_directory()
        self._set_umask()
        self._redirect_streams()

    def _redirect_streams(self):
        """Close and redirect standard streams."""
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()

        if self.err_log:
            sys.stderr = open(self.err_log, "a", self.BUFFERING)
        else:
            sys.stderr = NullDevice()

        if self.out_log:
            sys.stdout = open(self.out_log, "a", self.BUFFERING)
        else:
            sys.stdout = NullDevice()


def get_daemonize_class():
    """Return the appropriate daemonize class for the current OS."""
    if os.name == "posix":
        return PosixDaemonize
    return NonPosixDaemonize


def become_daemon(our_home_dir=".", out_log=None, err_log=None, umask=0o022):
    """Convenience function for backward compatibility.

    Turn the current process into a daemon.
    """
    daemonize_class = get_daemonize_class()
    daemon = daemonize_class(
        home_dir=our_home_dir,
        out_log=out_log,
        err_log=err_log,
        umask=umask,
    )
    daemon.daemonize()
