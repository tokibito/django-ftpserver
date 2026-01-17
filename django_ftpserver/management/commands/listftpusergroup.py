from django.core.management.base import BaseCommand

from django_ftpserver import models


class Command(BaseCommand):
    help = "List FTP user groups"

    def handle(self, *args, **options):
        groups = models.FTPUserGroup.objects.all().order_by("pk")

        if not groups.exists():
            self.stdout.write("No FTP user groups found.\n")
            return

        self.stdout.write("FTP User Groups:\n")
        self.stdout.write("-" * 60 + "\n")
        self.stdout.write(
            "{pk:<6} {name:<20} {permission:<10} {home_dir}\n".format(
                pk="ID", name="Name", permission="Permission", home_dir="Home Dir"
            )
        )
        self.stdout.write("-" * 60 + "\n")

        for group in groups:
            self.stdout.write(
                "{pk:<6} {name:<20} {permission:<10} {home_dir}\n".format(
                    pk=group.pk,
                    name=group.name,
                    permission=group.permission,
                    home_dir=group.home_dir or "",
                )
            )
