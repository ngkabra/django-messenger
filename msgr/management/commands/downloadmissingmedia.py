from msgr.models import MessageManager
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = None
    help = 'Downloads media for all messages that do not have media'

    def handle(self, *args, **options):
        try:
            mgr = MessageManager()
            successful_downloads, total_downloads = mgr.download_missing_media()
            self.stdout.write("Successfully downloaded {} of {} media.\n".format(successful_downloads, total_downloads))
        except Exception as e:
            raise CommandError('Failure! Error: %s' % e)


