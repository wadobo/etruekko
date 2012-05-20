from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from etruekko.truekko.models import Swap


class Command(BaseCommand):
    args = '<n>'
    help = 'Makes n swaps between users 1 and 2 and shows some info'

    def handle(self, *args, **options):
        try:
            n = int(args[0])
        except:
            raise CommandError("You need to provide the number of swaps")


        u1 = User.objects.get(pk=1)
        u2 = User.objects.get(pk=2)

        for i in range(n):
            print "\n-SWAP %s-\n" % i
            print "PRE %s - %s" % (u1, u1.get_profile().credits)
            print "PRE %s - %s" % (u2, u2.get_profile().credits)

            sw = Swap(user_from=u1,
                      user_to=u2,
                      status="CON")
            sw.save()
            sw.save()

            print "POS %s - %s" % (u1, u1.get_profile().credits)
            print "POS %s - %s" % (u2, u2.get_profile().credits)
