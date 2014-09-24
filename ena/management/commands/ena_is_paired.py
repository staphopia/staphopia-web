'''
    Robert Petit
    
    Determine if an experiment accession has paired reads or not.
'''
import os.path
from optparse import make_option

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from ena.models import Run

class Command(BaseCommand):
    help = 'Return the paired status of an experiment accession'

    option_list = BaseCommand.option_list + (
        make_option('--experiment', dest='experiment',
                    help='A table of experiment information.'),
        )
        
    def handle(self, *args, **options):
        # Required Parameters
        if not options['experiment']:
            raise CommandError('--experiment is requried')

        is_paired = 0
        runs = Run.objects.filter(
            experiment_accession = options['experiment']
        )

        if all([run.is_paired for run in runs]):
            print 1
        else:
            print 0