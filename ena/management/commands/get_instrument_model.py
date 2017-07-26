'''Get the instrument model of a given ENA experiment.'''
from django.core.management.base import BaseCommand

from ena.models import Experiment


class Command(BaseCommand):

    """ . """

    help = 'Get the instrument model of a given ENA experiment.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('experiment', help='Experiment to update.')

    def handle(self, *args, **options):
        try:
            experiment = Experiment.objects.get(
                experiment_accession=options['experiment']
            )
            print(experiment.instrument_model)
        except Experiment.DoesNotExist:
            print('{0} does not exist.'.format(options['experiment']))
