import sys

from django.core.management.base import BaseCommand, CommandError

from django_ftpserver import models
from django_ftpserver.compat import get_user_model, get_username_field


class Command(BaseCommand):
    help = "Create FTP user account"
    args = "username group [home_dir]"

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError("Enter the username and group name.")
        username = args[0]
        group_name = args[1]
        if len(args) > 2:
            home_dir = args[2]
        else:
            home_dir = None

        if models.FTPUserAccount.objects.filter(
                user__username=username).exists():
            raise CommandError(
                'FTP user account "{username}" is already exists.'.format(
                    username=username))

        User = get_user_model()
        try:
            user = User.objects.get(**{get_username_field(): username})
        except User.DoesNotExist:
            raise CommandError(
                'User "{username}" is not exists.'.format(username=username))

        try:
            group = models.FTPUserGroup.objects.get(name=group_name)
        except models.FTPUserGroup.DoesNotExist:
            raise CommandError(
                'FTP user group "{name}" is not exists.'.format(
                    name=group_name))

        account = models.FTPUserAccount.objects.create(
            user=user, group=group, home_dir=home_dir)

        sys.stdout.write(
            'FTP user account pk={pk}, "{username}" was created.\n'.format(
                pk=account.pk, username=username))
