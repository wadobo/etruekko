from django.core.management.base import BaseCommand, CommandError
from etruekko.truekko.models import Item, ItemImage


class Command(BaseCommand):
    help = 'Change photos from Item to ItemImage'

    def handle(self, *args, **options):
        for item in Item.objects.all():
            if item.photo:
                im = ItemImage(item=item, photo=item.photo)
                im.save()

