"""Update SNPs in the database."""
import sys
from cyvcf2 import VCF
import time

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from staphopia.utils import timeit
from variant.models import Reference, SNP


def get_reference_instance(reference_name):
    """Get reference instance."""
    try:
        return Reference.objects.get(name=reference_name)
    except IntegrityError:
        raise CommandError('Error getting/saving reference information')


class Command(BaseCommand):
    """Update SNPs in the database."""

    help = 'Update SNPs in the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('input', metavar='INPUT_VCF',
                            help=('Annotated VCF formated file to '
                                  'be inserted'))
        parser.add_argument('--compressed', action='store_true',
                            help='Input VCF is gzipped.')

    def handle(self, *args, **opts):
        """Insert results to database."""
        # Open VCF for reading
        try:
            vcf_reader = VCF(opts['input'])
        except IOError:
            raise CommandError('{0} does not exist'.format(input))

        # Get reference info
        reference_obj = get_reference_instance(vcf_reader.seqnames[0])

        # Read through VCF
        start_time = time.time()
        count = 0
        with connection.cursor() as cursor:
            for record in vcf_reader:
                if record.is_snp:
                    sql = """UPDATE variant_snp
                             SET reference_codon='{0}', alternate_codon='{1}',
                                 amino_acid_change='{2}'
                             WHERE reference_id={3} AND reference_position={4} AND
                                   alternate_base='{5}';""".format(
                        '.' if record.INFO['RefCodon'][0] is None else record.INFO['RefCodon'],
                        '.' if record.INFO['AltCodon'][0] is None else record.INFO['AltCodon'],
                        '.' if record.INFO['AminoAcidChange'][0] is None else record.INFO['AminoAcidChange'],
                        reference_obj.pk,
                        record.POS,
                        record.ALT[0]
                    )
                    cursor.execute(sql)
                    count += 1
                    if count % 100000 == 0:
                        total_time = f'{time.time() - start_time:.2f}'
                        rate = f'{100000 / float(total_time):.2f}'
                        print(''.join([
                            f'Processed 100k, Total {count} SNPs ',
                            f'(took {total_time}s, {rate} snp/s)'
                        ]))
                        start_time = time.time()
