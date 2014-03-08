import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from django_ftpserver import models


class Command(BaseCommand):
    help = "Create FTP user group"
    option_list = BaseCommand.option_list + (
        make_option('--permission', action='store', dest='permission',
                    help="permission for home directory."),)
    args = "name [home_dir]"

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError("Enter one group name.")
        name = args[0]
        if len(args) > 1:
            home_dir = args[1]
        else:
            home_dir = None

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
