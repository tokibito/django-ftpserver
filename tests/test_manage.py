import random
from io import StringIO

import pytest

from django.contrib.auth import get_user_model
from django.core import management
from django.core.management.base import CommandError

from django_ftpserver import models


class TestManage:
    def test_run_ftpserver(self):
        with pytest.raises(CommandError):
            # Test that management commands work - but without actually running one
            management.call_command("ftpserver", "--passive-ports=fake")

    @pytest.mark.django_db
    def test_createftpusergroup(self):
        random_name = "".join(random.choice("abcde") for _ in range(10))
        management.call_command("createftpusergroup", random_name)


class TestFTPUserGroupCommands:
    @pytest.mark.django_db
    def test_listftpusergroup_empty(self):
        out = StringIO()
        management.call_command("listftpusergroup", stdout=out)
        assert "No FTP user groups found" in out.getvalue()

    @pytest.mark.django_db
    def test_listftpusergroup_with_groups(self):
        models.FTPUserGroup.objects.create(name="testgroup1", permission="elr")
        models.FTPUserGroup.objects.create(
            name="testgroup2", permission="elradfmw", home_dir="/home/ftp"
        )

        out = StringIO()
        management.call_command("listftpusergroup", stdout=out)
        output = out.getvalue()

        assert "FTP User Groups:" in output
        assert "testgroup1" in output
        assert "testgroup2" in output
        assert "elr" in output
        assert "/home/ftp" in output

    @pytest.mark.django_db
    def test_deleteftpusergroup_success(self):
        models.FTPUserGroup.objects.create(name="deletegroup")

        out = StringIO()
        management.call_command("deleteftpusergroup", "deletegroup", stdout=out)

        assert "was deleted" in out.getvalue()
        assert not models.FTPUserGroup.objects.filter(name="deletegroup").exists()

    @pytest.mark.django_db
    def test_deleteftpusergroup_not_exists(self):
        with pytest.raises(CommandError) as exc_info:
            management.call_command("deleteftpusergroup", "nonexistent")
        assert "does not exist" in str(exc_info.value)

    @pytest.mark.django_db
    def test_deleteftpusergroup_has_accounts(self):
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpass")
        group = models.FTPUserGroup.objects.create(name="groupwithuser")
        models.FTPUserAccount.objects.create(user=user, group=group)

        with pytest.raises(CommandError) as exc_info:
            management.call_command("deleteftpusergroup", "groupwithuser")
        assert "has 1 user account(s)" in str(exc_info.value)


class TestFTPUserAccountCommands:
    @pytest.mark.django_db
    def test_listftpuseraccount_empty(self):
        out = StringIO()
        management.call_command("listftpuseraccount", stdout=out)
        assert "No FTP user accounts found" in out.getvalue()

    @pytest.mark.django_db
    def test_listftpuseraccount_with_accounts(self):
        User = get_user_model()
        user1 = User.objects.create_user(username="ftpuser1", password="pass1")
        user2 = User.objects.create_user(username="ftpuser2", password="pass2")
        group = models.FTPUserGroup.objects.create(name="ftpgroup")
        models.FTPUserAccount.objects.create(user=user1, group=group)
        models.FTPUserAccount.objects.create(
            user=user2, group=group, home_dir="/home/ftpuser2"
        )

        out = StringIO()
        management.call_command("listftpuseraccount", stdout=out)
        output = out.getvalue()

        assert "FTP User Accounts:" in output
        assert "ftpuser1" in output
        assert "ftpuser2" in output
        assert "ftpgroup" in output
        assert "/home/ftpuser2" in output

    @pytest.mark.django_db
    def test_deleteftpuseraccount_success(self):
        User = get_user_model()
        user = User.objects.create_user(username="deleteuser", password="pass")
        group = models.FTPUserGroup.objects.create(name="delgroup")
        models.FTPUserAccount.objects.create(user=user, group=group)

        out = StringIO()
        management.call_command("deleteftpuseraccount", "deleteuser", stdout=out)

        assert "was deleted" in out.getvalue()
        assert not models.FTPUserAccount.objects.filter(user=user).exists()

    @pytest.mark.django_db
    def test_deleteftpuseraccount_user_not_exists(self):
        with pytest.raises(CommandError) as exc_info:
            management.call_command("deleteftpuseraccount", "nonexistentuser")
        assert "does not exist" in str(exc_info.value)

    @pytest.mark.django_db
    def test_deleteftpuseraccount_account_not_exists(self):
        User = get_user_model()
        User.objects.create_user(username="userwithnoaccount", password="pass")

        with pytest.raises(CommandError) as exc_info:
            management.call_command("deleteftpuseraccount", "userwithnoaccount")
        assert "does not exist" in str(exc_info.value)

    @pytest.mark.django_db
    def test_createftpuseraccount(self):
        User = get_user_model()
        user = User.objects.create_user(username="newftpuser", password="pass")
        models.FTPUserGroup.objects.create(name="newgroup")

        out = StringIO()
        management.call_command(
            "createftpuseraccount", "newftpuser", "newgroup", stdout=out
        )

        assert "was created" in out.getvalue()
        assert models.FTPUserAccount.objects.filter(user=user).exists()
