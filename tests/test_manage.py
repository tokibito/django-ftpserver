
from django.core import management
from django.core.management.base import CommandError
from unittest import TestCase


class ManageTestCase(TestCase):
    def test_run_ftpserver(self):
        # Test that management commands work - but without actually running one
        with self.assertRaises(CommandError):
            management.call_command('ftpserver', '--passive-ports=fake')