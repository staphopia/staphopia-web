""" Print SCCmec status by ST. """
from django.core.management.base import BaseCommand

from mlst.models import Srst2
from variant.models import ToSNP


class Command(BaseCommand):

    """ Print SCCmec status by ST.. """

    help = 'Print SCCmec status by ST.'

    def handle(self, *args, **opts):
        """ Print SCCmec status by ST.. """
        status = {'undetermined': {
            'pos': 0,
            'neg': 0,
        }}

        for mlst in Srst2.objects.filter():
            st = 'undetermined'
            if mlst.is_exact:
                st = mlst.st_stripped
                if st not in status:
                    status[mlst.st_stripped] = {
                        'pos': 0,
                        'neg': 0,
                    }

            s80f = ToSNP.objects.filter(
                sample=mlst.sample,
                snp_id=4069689
            ).count()

            s84l = ToSNP.objects.filter(
                sample=mlst.sample,
                snp_id=21765
            ).count()

            if s80f or s84l:
                status[st]['pos'] += 1
            else:
                status[st]['neg'] += 1

        for key, val in status.items():
            freq_pos = float(val['pos']) / (val['pos'] + val['neg'])
            print '{0}\t{1}\t{2}\t{3:.2f}'.format(
                key, val['pos'], val['neg'], freq_pos
            )
