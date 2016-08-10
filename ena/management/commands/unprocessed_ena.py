"""Insert ENA data information into the database."""
try:
    import ujson as json
except ImportError:
    import json

from django.core.management.base import BaseCommand

from ena.models import Experiment, Run, ToSample, ToPublication


class Command(BaseCommand):
    """Insert ENA data information into the database."""

    help = 'Insert ENA data information into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument(
            '--limit', dest='limit', type=int, default=10 ** 11,
            help='Limit the number of experiments to output.'
        )
        parser.add_argument(
            '--technology', dest='technology',
            help=('Filter results by a certain technology. (ILLUMINA, '
                  'LS454, PACBIO_SMRT, ION_TORRENT, ABI_SOLID)')
        )
        parser.add_argument('--coverage', dest='coverage', type=int, default=0,
                            help='Filter results based on coverage.')
        parser.add_argument(
            '--min_read_length', dest='min_read_length', type=int, default=0,
            help='Filter results based on minimum read length.'
        )
        parser.add_argument(
            '--max_read_length', dest='max_read_length', default=10 ** 11,
            type=int, help='Filter results based on maximum read length.'
        )
        parser.add_argument(
            '--experiment', dest='experiment',
            help='Filter results based on experiment accession.'
        )
        parser.add_argument('--study', dest='study', type=str, default=None,
                            help='Filter results based on study accession.')
        parser.add_argument('--column', dest='column',
                            help='Filter results based on specific column.')
        parser.add_argument(
            '--accessions', dest='accessions',
            help=('Filter results based on accessions specific to a'
                  ' column.')
        )
        parser.add_argument(
            '--published', dest='published', action='store_true',
            help='Filter results based on published samples'
        )

    def handle(self, *args, **options):
        """Get unproccessed samples."""
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
            ena_entries = ena_entries.filter(
                instrument_platform=options['technology']
            )

        if options['coverage']:
            ena_entries = ena_entries.filter(
                coverage__gte=options['coverage']
            ).order_by('coverage')

        if options['published']:
            pubs = ToPublication.objects.values_list(
                'experiment_accession', flat=True
            ).order_by('experiment_accession')
            ena_entries = ena_entries.filter(
                experiment_accession__in=list(pubs)
            )

        # Get Run info
        to_process = {}
        for e in ena_entries:
            if len(to_process) >= int(options['limit']):
                break
            else:
                ena_runs = Run.objects.filter(
                    experiment_accession=e.experiment_accession,
                    mean_read_length__range=(
                        options['min_read_length'],
                        options['max_read_length']
                    )
                )
                if ena_runs.count() > 0:
                    to_process[e.experiment_accession] = {}
                    for r in ena_runs:
                        to_process[e.experiment_accession][r.run_accession] = {
                            'is_paired': r.is_paired,
                            'technology': e.instrument_platform,
                            'coverage': e.coverage,
                            'fastq_ftp': r.fastq_ftp.split(';'),
                            'fastq_aspera': r.fastq_aspera.split(';'),
                            'fastq_md5': r.fastq_md5.split(';')
                        }
        print(json.dumps(to_process))
