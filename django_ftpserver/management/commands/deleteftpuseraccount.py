from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from django_ftpserver import models


class Command(BaseCommand):
    help = "Delete FTP user account"

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **options):
        username = options.get("username")

        User = get_user_model()
        try:
            user = User.objects.get(**{User.USERNAME_FIELD: username})
        except User.DoesNotExist:
            raise CommandError(
                'User "{username}" does not exist.'.format(username=username)
            )

        try:
            account = models.FTPUserAccount.objects.get(user=user)
        except models.FTPUserAccount.DoesNotExist:
            raise CommandError(
                'FTP user account for "{username}" does not exist.'.format(
                    username=username
                )
            )

        pk = account.pk
        account.delete()

        self.stdout.write(
            'FTP user account pk={pk}, "{username}" was deleted.\n'.format(
                pk=pk, username=username
            )
        )
