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
        status = {'undetermined': {
            'MSSA': 0,
            'MRSA': 0,
        }}

        for mlst in Srst2.objects.filter():
            st = 'undetermined'
            if mlst.is_exact:
                st = mlst.st_stripped
                if st not in status:
                    status[mlst.st_stripped] = {
                        'MSSA': 0,
                        'MRSA': 0,
                    }

            meca = Coverage.objects.filter(
                sample=mlst.sample,
                meca_total__gte=opts['cutoff']
            ).count()

            if meca:
                status[st]['MRSA'] += 1
            else:
                status[st]['MSSA'] += 1

        for key, val in status.items():
            freq_mrsa = float(val['MRSA']) / (val['MRSA'] + val['MSSA'])
            print '{0}\t{1}\t{2}\t{3:.2f}'.format(
                key, val['MRSA'], val['MSSA'], freq_mrsa
            )
