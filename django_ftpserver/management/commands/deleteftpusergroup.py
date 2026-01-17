from django.core.management.base import BaseCommand, CommandError

from django_ftpserver import models


class Command(BaseCommand):
    help = "Delete FTP user group"

    def add_arguments(self, parser):
        parser.add_argument("name")

    def handle(self, *args, **options):
        name = options.get("name")

        try:
            group = models.FTPUserGroup.objects.get(name=name)
        except models.FTPUserGroup.DoesNotExist:
            raise CommandError(
                'FTP user group "{name}" does not exist.'.format(name=name)
            )

        account_count = models.FTPUserAccount.objects.filter(group=group).count()
        if account_count > 0:
            raise CommandError(
                'FTP user group "{name}" has {count} user account(s). '
                "Delete them first.".format(name=name, count=account_count)
            )

        pk = group.pk
        group.delete()

        self.stdout.write(
            'FTP user group pk={pk}, "{name}" was deleted.\n'.format(pk=pk, name=name)
        )
