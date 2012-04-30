from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from etruekko.truekko.models import Item

import random


desc = 'Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio. Maecenas convallis ullamcorper ultricies. Curabitur ornare, ligula semper consectetur sagittis, nisi diam iaculis velit, id fringilla sem nunc vel mi. Nam dictum, odio nec pretium volutpat, arcu ante placerat erat, non tristique elit urna et turpis. Quisque mi metus, ornare sit amet fermentum et, tincidunt et orci. Fusce eget orci a orci congue vestibulum. Ut dolor diam, elementum et vestibulum eu, porttitor vel elit. Curabitur venenatis pulvinar tellus gravida ornare. Sed et erat faucibus nunc euismod ultricies ut id justo. Nullam cursus suscipit nisi, et ultrices justo sodales nec. Fusce venenatis facilisis lectus ac semper. Aliquam at massa ipsum. Quisque bibendum purus convallis nulla ultrices ultricies. Nullam aliquam, mi eu aliquam tincidunt, purus velit laoreet tortor, viverra pretium nisi quam vitae mi. Fusce vel volutpat elit. Nam sagittis nisi dui.'.split(' ')


class Command(BaseCommand):
    args = '<n>'
    help = 'Adds n test items'

    def handle(self, *args, **options):
        try:
            n = int(args[0])
        except:
            raise CommandError("You need to provide the number of items to add")


        for i in range(n):
            users = list(User.objects.all()[0:10])
            item = Item(user=random.choice(users),
                        type=random.choice(['IT', 'SR']),
                        offer_or_demand=random.choice(['OFF', 'DEM']),
                        name="item %s" % (i + 1),
                        description=' '.join(random.choice(desc) for i in range(80)),
                        price=random.choice(range(1,11)))
            item.save()
