import sys

from django.core.management.base import BaseCommand, CommandError

from django_ftpserver import models


class Command(BaseCommand):
    help = "Create FTP user group"

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('home_dir', nargs='?')

        parser.add_argument(
            '--permission', action='store', dest='permission',
            help="permission for home directory.")

    def handle(self, *args, **options):
        name = options.get('name')
        home_dir = options.get('home_dir')

        if models.FTPUserGroup.objects.filter(name=name).exists():
            raise CommandError(
                "FTP user group {name} is already exists.".format(name=name))

        group = models.FTPUserGroup(name=name, home_dir=home_dir)
        if options['permission']:
            group.permission = options['permission']
        group.save()

        sys.stdout.write(
            "FTP user group pk={pk}, {name} was created.\n".format(
                pk=group.pk, name=name))
