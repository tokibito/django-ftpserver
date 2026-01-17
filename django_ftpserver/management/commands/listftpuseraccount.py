from django.core.management.base import BaseCommand

from django_ftpserver import models


class Command(BaseCommand):
    help = "List FTP user accounts"

    def handle(self, *args, **options):
        accounts = models.FTPUserAccount.objects.select_related(
            "user", "group"
        ).order_by("pk")

        if not accounts.exists():
            self.stdout.write("No FTP user accounts found.\n")
            return

        self.stdout.write("FTP User Accounts:\n")
        self.stdout.write("-" * 80 + "\n")
        self.stdout.write(
            "{pk:<6} {username:<20} {group:<20} {home_dir}\n".format(
                pk="ID", username="Username", group="Group", home_dir="Home Dir"
            )
        )
        self.stdout.write("-" * 80 + "\n")

        for account in accounts:
            self.stdout.write(
                "{pk:<6} {username:<20} {group:<20} {home_dir}\n".format(
                    pk=account.pk,
                    username=account.get_username(),
                    group=account.group.name if account.group else "",
                    home_dir=account.home_dir or "",
                )
            )
