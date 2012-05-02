from django.core.management.base import BaseCommand, CommandError
from etruekko.truekko.models import Channel


channels = (
    ('Ayuntamientos', 'Canal dedicado a ayuntamientos'),
    ('Asociaciones', 'Canal dedicado a asociaciones y agrupaciones'),
    ('ONG', 'Canal dedicado a organizaciones no gubernamentales'),
)


class Command(BaseCommand):
    help = 'Adds default truekko channels'

    def handle(self, *args, **options):
        for n, d in channels:
            c = Channel(name=n, description=d)
            c.save()
