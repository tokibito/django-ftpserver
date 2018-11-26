import pytest

from django.core import management
from django.core.management.base import CommandError
from unittest import TestCase
import random


class TestManage:
    def test_run_ftpserver(self):
        with pytest.raises(CommandError):
            # Test that management commands work - but without actually running one
            management.call_command('ftpserver', '--passive-ports=fake')
    
    @pytest.mark.django_db
    def test_createftpusergroup(self):
        random_name = ''.join(random.choice('abcde') for _ in range(10))
        management.call_command('createftpusergroup', random_name)
