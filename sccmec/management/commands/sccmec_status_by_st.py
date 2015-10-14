""" Print SCCmec status by ST. """
from django.core.management.base import BaseCommand

from mlst.models import Srst2
from sccmec.models import Coverage


class Command(BaseCommand):

    """ Print SCCmec status by ST.. """

    help = 'Print SCCmec status by ST.'

    def add_arguments(self, parser):
        """ Make some arguements. """
        parser.add_argument('--cutoff', metavar='CUTOFF', type=float,
                            default=0.70,
                            help=('Percent coverage cutoff for positive mecA.'
                                  ' Default (0.70)'))

    def handle(self, *args, **opts):
        """ Print SCCmec status by ST.. """
        st = {}

        for mlst in Srst2.objects.filter(is_exact=True):
            if mlst.st_stripped not in st:
                st[mlst.st_stripped] = {
                    'MSSA': 0,
                    'MRSA': 0,
                }

            meca = Coverage.objects.filter(
                sample=mlst.sample,
                meca_total__gte=opts['cutoff']
            ).count()

            if meca:
                st[mlst.st_stripped]['MRSA'] += 1
            else:
                st[mlst.st_stripped]['MSSA'] += 1

        for key, val in st.items():
            print '{0}\t{1}\t{2}'.format(key, val['MRSA'], val['MSSA'])
