"""Insert SCCmec cassettes used for mapping into database."""
import os.path

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from sccmec.models import Cassette
from staphopia.utils import read_fasta


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert SCCmec cassettes used for mapping into database.'

    def add_arguments(self, parser):
        """Make some arguements."""
        parser.add_argument('fasta', metavar='FASTA',
                            help='FASTA file used to create BWA database.')
        parser.add_argument('meca', metavar='MECA_POSTITIONS',
                            help='Text file with headers and mecA positions.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert results to database."""
        if not os.path.exists(opts['fasta']):
            raise CommandError('{0} does not exist'.format(opts['fasta']))
        elif not os.path.exists(opts['meca']):
            raise CommandError('{0} does not exist'.format(opts['meca']))

        meca = {}
        with open(opts['meca'], "r") as f:
            for line in f:
                line = line.rstrip()
                header, positions = line.split(' ')
                start, stop = positions.split('..')
                meca[header] = {
                    'start': int(start),
                    'stop': int(stop),
                    'length': (int(stop) - int(start))
                }

        seqs = read_fasta(opts['fasta'])
        for header, seq in seqs.items():
            cassette_id = header.split('|')[0]
            cassette, created = Cassette.objects.get_or_create(
                name=cassette_id,
                header=header,
                length=len(seq),
                meca_start=meca[header]['start'],
                meca_stop=meca[header]['stop'],
                meca_length=meca[header]['length'],
            )

            print('{0}\t{1}'.format(header, created))
