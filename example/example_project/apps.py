"""
AppConfig for example_project with auto-setup functionality.
"""

import sys
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings


class ExampleProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "example_project"

    def ready(self):
        # Only run setup during runserver or ftpserver commands
        if not any(cmd in sys.argv for cmd in ["runserver", "ftpserver"]):
            return

        # Avoid running twice in auto-reload
        import os

        if os.environ.get("RUN_MAIN") != "true" and "runserver" in sys.argv:
            return

        self._setup_demo_user()
        self._setup_data_directory()

    def _setup_demo_user(self):
        """Create demo user and FTP account if they don't exist."""
        from django.contrib.auth import get_user_model
        from django.db import connection

        # Check if migrations have been applied
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name='auth_user'"
                )
                if not cursor.fetchone():
                    return
        except Exception:
            return

        User = get_user_model()

        try:
            user = User.objects.filter(username="demo").first()
            if user is None:
                # Create superuser with demo/demo credentials
                user = User.objects.create_superuser(
                    username="demo",
                    email="demo@example.com",
                    password="demo",
                )

                # Create FTP group and account
                self._setup_ftp_account(user)

                # Print credentials
                print()
                print("=" * 50)
                print("Demo user created!")
                print("  Username: demo")
                print("  Password: demo")
                print("=" * 50)
                print()
                sys.stdout.flush()
        except Exception:
            # Silently ignore errors (e.g., migrations not applied)
            pass

    def _setup_ftp_account(self, user):
        """Create FTP group and account for the user."""
        from django_ftpserver.models import FTPUserAccount, FTPUserGroup

        data_dir = str(Path(settings.DATA_DIR).resolve())

        # Create or get FTP group
        group, _ = FTPUserGroup.objects.get_or_create(
            name="demo-group",
            defaults={
                "home_dir": data_dir,
                "permission": "elradfmw",
            },
        )

        # Create FTP account
        FTPUserAccount.objects.get_or_create(
            user=user,
            defaults={
                "group": group,
                "home_dir": data_dir,
            },
        )

    def _setup_data_directory(self):
        """Ensure data directory exists."""
        data_dir = Path(settings.DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
