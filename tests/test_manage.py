
from django.core import management
from django.core.management.base import CommandError
from unittest import TestCase
import random


class ManageTestCase(TestCase):
    def test_run_ftpserver(self):
        # Test that management commands work - but without actually running one
        with self.assertRaises(CommandError):
            management.call_command('ftpserver', '--passive-ports=fake')
    
    def test_createftpusergroup(self):
        random_name = ''.join(random.choice('abcde') for _ in range(10))
        management.call_command('createftpusergroup', random_name)