from django.core.management.base import BaseCommand, CommandError

from django_ftpserver import models


def non_existent_user_group(name):
    if models.FTPUserGroup.objects.filter(name=name).exists():
        raise CommandError(f"FTP user group {name} is already exists.")
    else:
        return name


class Command(BaseCommand):
    help = "Create FTP user group"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "name",
            type=non_existent_user_group,
        )

        parser.add_argument(
            "--main_directory",
            action="store",
            dest="mainly_directory",
            help="Mainly directory.",
        )
        parser.add_argument(
            "--permission",
            action="store",
            dest="permission",
            help="permission for home directory.",
        )

    def handle(self, *args, **options):
        name = options.get("name")
        main_directory = options.get("main_directory")
        home_dir = f"{f'/{main_directory}' if main_directory else ''}/{name}"
        group = models.FTPUserGroup(name=name, home_dir=home_dir)
        if options["permission"]:
            group.permission = options["permission"]
        group.save()

        self.stdout.write(f"FTP user group pk={group.pk}, {name} was created.\n")
