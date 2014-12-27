'''
    Robert Petit

    Outputs Experiments and corresponding runs information in JSON format.
'''
import json
from optparse import make_option

from django.core.management.base import BaseCommand

from ena.models import Experiment, Run, ToSample


class Command(BaseCommand):

    """ . """

    help = 'Insert ENA data information into the database.'

    option_list = BaseCommand.option_list + (
        make_option('--limit', dest='limit',
                    help='Limit the number of experiments to output.'),
        make_option('--technology', dest='technology',
                    help=('Filter results by a certain technology. (ILLUMINA, '
                          'LS454, PACBIO_SMRT, ION_TORRENT, ABI_SOLID)')),
        make_option('--coverage', dest='coverage',
                    help='Filter results based on coverage.'),
        make_option('--min_read_length', dest='min_read_length',
                    help='Filter results based on minimum read length.'),
        make_option('--max_read_length', dest='max_read_length',
                    help='Filter results based on maximum read length.'),
        make_option('--experiment', dest='experiment',
                    help='Filter results based on experiment accession.'),
    )

    def handle(self, *args, **opts):
        # Required Parameters
        if not opts['limit']:
            opts['limit'] = 10 ** 11
        if not opts['coverage']:
            opts['coverage'] = 0
        if not opts['min_read_length']:
            opts['min_read_length'] = 0
        if not opts['max_read_length']:
            opts['max_read_length'] = 10 ** 11
        if not opts['experiment']:
            opts['experiment'] = None

        # ENA to Sample
        ena_to_sample = ToSample.objects.values_list(
            'experiment_accession', flat=True
        ).order_by('experiment_accession')

        # Get Experiments not in ToSample
        ena_entries = None
        if opts['experiment']:
            ena_entries = Experiment.objects.exclude(
                experiment_accession__in=ena_to_sample,
            ).filter(experiment_accession=opts['experiment'])
        elif opts['technology']:
            ena_entries = Experiment.objects.exclude(
                experiment_accession__in=ena_to_sample,
            ).filter(instrument_platform=opts['technology'])
        else:
            ena_entries = Experiment.objects.exclude(
                experiment_accession__in=ena_to_sample,
            )

        # Get Run info
        to_process = {}
        for entry in ena_entries:
            if len(to_process) >= int(opts['limit']):
                break
            else:
                ena_runs = Run.objects.filter(
                    experiment_accession=entry.experiment_accession,
                    mean_read_length__range=(
                        opts['min_read_length'],
                        opts['max_read_length']
                    )
                )
                if ena_runs.count() > 0:
                    coverage = sum([float(r.coverage) for r in ena_runs])
                    if coverage > float(opts['coverage']):
                        to_process[entry.experiment_accession] = {}
                        for run in ena_runs:
                            to_process[entry.experiment_accession][run.run_accession] = {
                                'is_paired': run.is_paired,
                                'fastq_ftp': run.fastq_ftp,
                                'fastq_aspera': run.fastq_aspera,
                            }

        print json.dumps(to_process)
