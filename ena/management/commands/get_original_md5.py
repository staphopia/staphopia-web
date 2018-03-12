'''Get the original fastq MD5s of a given ENA experiment.'''
import sys

from django.core.management.base import BaseCommand

from ena.models import Run


class Command(BaseCommand):

    """ . """

    help = 'Get the original fastq MD5s of a given ENA experiment.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('experiment', help='Experiment to get MD5 for.')
        parser.add_argument('output', help='File to write MD5s to.')
        parser.add_argument('--quiet', action='store_true',
                            help='Will not output error on multiple runs.')

    def handle(self, *args, **options):
        run = None
        try:
            run = Run.objects.get(
                experiment_accession=options['experiment']
            )
            print(f'Outputting MD5s for {options["experiment"]}')
        except Run.MultipleObjectsReturned:
            if not options['quiet']:
                print(f'{options["experiment"]} consists of multiple runs',
                      file=sys.stderr)

        if run:
            with open(options["output"], 'w') as fh:
                for md5 in run.fastq_md5.split(';'):
                    if md5:
                        fh.write(f'{md5}\n')
