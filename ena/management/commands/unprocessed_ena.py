"""Insert ENA data information into the database."""
try:
    import ujson as json
except ImportError:
    import json

from django.core.management.base import BaseCommand

from ena.models import Experiment, Run, ToSample


class Command(BaseCommand):
    """Insert ENA data information into the database."""

    help = 'Insert ENA data information into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument(
            '--limit', dest='limit',
            help='Limit the number of experiments to output.'
        )
        parser.add_argument(
            '--technology', dest='technology',
            help=('Filter results by a certain technology. (ILLUMINA, '
                  'LS454, PACBIO_SMRT, ION_TORRENT, ABI_SOLID)')
        )
        parser.add_argument('--coverage', dest='coverage',
                            help='Filter results based on coverage.')
        parser.add_argument(
            '--min_read_length', dest='min_read_length',
            help='Filter results based on minimum read length.'
        )
        parser.add_argument(
            '--max_read_length', dest='max_read_length',
            help='Filter results based on maximum read length.'
        )
        parser.add_argument(
            '--experiment', dest='experiment',
            help='Filter results based on experiment accession.'
        )
        parser.add_argument('--study', dest='study',
                            help='Filter results based on study accession.')
        parser.add_argument('--column', dest='column',
                            help='Filter results based on specific column.')
        parser.add_argument(
            '--accessions', dest='accessions',
            help=('Filter results based on accessions specific to a'
                  ' column.')
        )

    def handle(self, *args, **options):
        # Required Parameters
        if not options['limit']:
            options['limit'] = 10 ** 11
        if not options['coverage']:
            options['coverage'] = 0
        if not options['min_read_length']:
            options['min_read_length'] = 0
        if not options['max_read_length']:
            options['max_read_length'] = 10 ** 11
        if not options['experiment']:
            options['experiment'] = None

        # ENA to Sample
        ena_to_sample = ToSample.objects.values_list(
            'experiment_accession', flat=True
        ).order_by('experiment_accession')

        # Get Experiments not in ToSample
        ena_entries = None
        if options['experiment']:
            ena_entries = Experiment.objects.exclude(
                experiment_accession__in=ena_to_sample,
            ).filter(experiment_accession=options['experiment'])
        elif options['study']:
            ena_entries = Experiment.objects.exclude(
                experiment_accession__in=ena_to_sample,
            ).filter(study_accession=options['study'])
        elif options['column'] and options['accessions']:
            with open(options['accessions'], 'r') as fh:
                accessions = []
                for line in fh:
                    accessions.append(line.rstrip())
                ena_entries = Experiment.objects.exclude(
                    experiment_accession__in=ena_to_sample,
                ).filter(
                    secondary_sample_accession__in=accessions
                )
        else:
            ena_entries = Experiment.objects.exclude(
                experiment_accession__in=ena_to_sample,
            )

        if options['technology']:
            ena_entries = ena_entries.filter(instrument_platform=options['technology'])

        if options['coverage']:
            ena_entries = ena_entries.filter(coverage__gte=options['coverage']).order_by('coverage')

        # Get Run info
        to_process = {}
        for entry in ena_entries:
            if len(to_process) >= int(options['limit']):
                break
            else:
                ena_runs = Run.objects.filter(
                    experiment_accession=entry.experiment_accession,
                    mean_read_length__range=(
                        options['min_read_length'],
                        options['max_read_length']
                    )
                )
                if ena_runs.count() > 0:
                    to_process[entry.experiment_accession] = {}
                    for run in ena_runs:
                        to_process[entry.experiment_accession][run.run_accession] = {
                            'is_paired': run.is_paired,
                            'technology': entry.instrument_platform,
                            'coverage': entry.coverage,
                            'fastq_ftp': run.fastq_ftp.split(';'),
                            'fastq_aspera': run.fastq_aspera.split(';'),
                            'fastq_md5': run.fastq_md5.split(';')
                        }
        print json.dumps(to_process)
