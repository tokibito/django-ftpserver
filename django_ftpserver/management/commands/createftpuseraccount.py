from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from django_ftpserver import models
from django_ftpserver.compat import get_username_field


def non_existent_user_account(username):
    if models.FTPUserAccount.objects.filter(user__username=username).exists():
        raise CommandError(f"FTP user group {username} is already exists.")
    else:
        return username


class Command(BaseCommand):
    help = "Create FTP user account"

    def add_arguments(self, parser):
        parser.add_argument("username", type=non_existent_user_account)
        parser.add_argument("group")

    def handle(self, *args, **options):
        username = options.get("username")
        group_name = options.get("group")

        User = get_user_model()
        try:
            user = User.objects.get(**{get_username_field(): username})
        except User.DoesNotExist:
            raise CommandError(
                'User "{username}" is not exists.'.format(username=username)
            )

        try:
            group = models.FTPUserGroup.objects.get(name=group_name)
        except models.FTPUserGroup.DoesNotExist:
            raise CommandError(
                'FTP user group "{name}" is not exists.'.format(name=group_name)
            )
        main_directory = options.get("main_directory")
        home_dir = f"{f'/{main_directory}' if main_directory else ''}/{username}"
        account = models.FTPUserAccount.objects.create(
            user=user, group=group, home_dir=home_dir
        )

        self.stdout.write(
            'FTP user account pk={pk}, "{username}" was created.\n'.format(
                pk=account.pk, username=username
            )
        )
