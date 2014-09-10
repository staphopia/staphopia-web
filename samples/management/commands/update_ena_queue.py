'''

'''
import os.path
from optparse import make_option

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from samples.models.ena import *

class Command(BaseCommand):
    help = 'Insert experiments without a sample id into the queue.'
    
    @transaction.atomic 
    def handle(self, *args, **options):
        # Experiments
        ena_experiment = EnaExperiment.objects.values_list(
            'experiment_accession', flat=True
        ).order_by('experiment_accession')

        # ENA to Sample
        ena_to_sample = EnaToSample.objects.values_list(
            'experiment_accession', flat=True
        ).order_by('experiment_accession')
        
        # Queue
        ena_queue = EnaQueue.objects.values_list(
            'experiment_accession', flat=True
        ).order_by('experiment_accession')
       
        added_to_queue = 0
        for exp in ena_experiment:

            if (exp not in ena_to_sample) and (exp not in ena_queue):
                # Add to queue
                exp = EnaExperiment.objects.get(pk=exp)
                queue = EnaQueue(experiment_accession=exp, is_waiting=True)
                queue.save() 
                added_to_queue += 1

        print 'Total Experiments: {0}'.format(len(ena_experiment))
        print 'Total Experiments With Sample ID: {0}'.format(len(ena_to_sample))
        print 'Total Experiments In Queue: {0}'.format(len(ena_queue))
        print 'Total Experiments Added To Queue: {0}'.format(added_to_queue)