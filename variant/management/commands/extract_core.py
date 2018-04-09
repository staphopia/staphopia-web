"""Insert variant analysis results into database."""
from collections import OrderedDict
import glob

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from staphopia.utils import read_fasta
from api.utils import query_database


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('valid', metavar='VALIDATED_GENES',
                            help=('Annotation IDs to be used.'))
        parser.add_argument('directory', metavar='DIRECTORY',
                            help=('Directory with extract_genome output.'))

    def handle(self, *args, **opts):
        """Insert results to database."""
        # Valid set of Annotation IDs
        valid = {}
        with open(opts['valid'], 'r') as fh:
            for line in fh:
                valid[line.rstrip()] = True

        # Read extract_genome output
        samples = {}
        lengths = {}
        for fasta in glob.glob(f'{opts["directory"]}/*annotation.fasta'):
            merged_sequence = []
            st = None
            sample_name = None
            for header, sequence in read_fasta(fasta).items():
                sample, name, annotation_id, locus, length = header.split('|')
                if not st:
                    st = query_database(
                        f'SELECT * FROM sample_basic WHERE sample_id={sample}'
                    )[0]['st']
                    sample_name = f'{sample}|{name}|ST{st}'

                if annotation_id in valid:
                    merged_sequence.append(sequence)

            if merged_sequence:
                samples[sample_name] = ''.join(merged_sequence)
                lengths[len(samples[sample_name])] = True

        if len(lengths) == 1:
            length = list(lengths.keys())[0]
            print(f'Merged {len(valid)} genes (length={length}bp)')
            with open('extract-core.phylip', 'w') as phylip_output, \
                    open('extract-core.fasta', 'w') as fasta_output:
                phylip_output.write(f'{len(samples)} {length}\n')
                for header, sequence in samples.items():
                    fasta_output.write(f'>{header}\n')
                    fasta_output.write(f'{sequence}\n')
                    phylip_output.write(f'{header}\t{sequence}\n')
        else:
            raise CommandError('Multiple lengths: {length.keys()}')
