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
        parser.add_argument('dir', metavar='DIRECTORY',
                            help=('Directory with extract_genome output.'))

    def handle(self, *args, **opts):
        """Insert results to database."""
        # Produce Stats
        stats = OrderedDict()
        samples = OrderedDict()
        for details in glob.glob(f'{opts["dir"]}/*annotation-details.txt'):
            with open(details, 'r') as detail:
                for line in detail:
                    # Columns: sample_id, annotation_id, has_zero_count,
                    #          total_snps, total_indels, total_variants
                    line = line.rstrip()
                    if line.startswith('sample_id'):
                        continue
                    else:
                        cols = line.split('\t')
                        if cols[0] not in samples:
                            samples[cols[0]] = {
                                'sample_id': cols[0],
                                'annotation_zero_count': 0,
                                'annotation_zero': 0,
                                'annotation_snps': 0,
                                'annotation_indels': 0,
                                'zero_snps': 0,
                                'zero_indels': 0,
                                'zero_annotation': 0,
                                'total_snps': 0,
                                'total_indels': 0
                            }

                        if cols[1] not in stats:
                            stats[cols[1]] = {
                                'annotation_id': cols[1],
                                'has_zero_count': False,
                                'samples_zero_count': 0,
                                'sample_zero': 0,
                                'sample_snps': 0,
                                'sample_indels': 0,
                                'zero_snps': 0,
                                'zero_indels': 0,
                                'zero_annotation': 0,
                                'total_snps': 0,
                                'total_indels': 0
                            }

                        if cols[2] == 'True':
                            samples[cols[0]]['annotation_zero_count'] += 1
                            stats[cols[1]]['samples_zero_count'] += 1
                            stats[cols[1]]['has_zero_count'] = True
                            if not int(cols[5]):
                                samples[cols[0]]['zero_snps'] += 1
                                samples[cols[0]]['zero_indels'] += 1
                                samples[cols[0]]['zero_annotation'] += 1
                                stats[cols[1]]['zero_snps'] += 1
                                stats[cols[1]]['zero_indels'] += 1
                                stats[cols[1]]['zero_annotation'] += 1
                            else:
                                samples[cols[0]]['annotation_zero'] += 1
                                samples[cols[0]]['annotation_snps'] += 1
                                samples[cols[0]]['annotation_indels'] += 1
                                stats[cols[1]]['sample_zero'] += 1
                                stats[cols[1]]['sample_snps'] += 1
                                stats[cols[1]]['sample_indels'] += 1

                        samples[cols[0]]['total_snps'] += int(cols[3])
                        samples[cols[0]]['total_indels'] += int(cols[4])
                        stats[cols[1]]['total_snps'] += int(cols[3])
                        stats[cols[1]]['total_indels'] += int(cols[4])


        with open('extract-genome-sample.txt', 'w') as output:
            cols = [
                'sample_id', 'annotation_zero_count', 'annotation_zero',
                'annotation_snps', 'annotation_indels', 'zero_snps',
                'zero_indels', 'zero_annotation', 'total_snps', 'total_indels'
            ]
            output.write('{0}\n'.format('\t'.join(cols)))
            for sample, details in samples.items():
                output.write('{0}\n'.format(
                   '\t'.join([str(details[col]) for col in cols])
                ))

        with open('extract-genome-annotation.txt', 'w') as output:
            cols = [
                'annotation_id', 'has_zero_count', 'samples_zero_count',
                'sample_zero', 'sample_snps', 'sample_indels', 'zero_snps',
                'zero_indels', 'zero_annotation', 'total_snps', 'total_indels'
            ]
            output.write('{0}\n'.format('\t'.join(cols)))
            for annotation, details in stats.items():
                output.write('{0}\n'.format(
                   '\t'.join([str(details[col]) for col in cols])
                ))
