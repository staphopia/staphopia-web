'''
    Robert Petit
    
    Determine if an experiment accession has paired reads or not.
'''
import sys
import json
import os.path
from optparse import make_option

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from ena.models import Experiment, ToSample
from samples.models import Sample

class Command(BaseCommand):
    help = 'Return the paired status of an experiment accession'

    option_list = BaseCommand.option_list + (
        make_option('--experiment', dest='experiment',
                    help='A table of experiment information.'),
        make_option('--is_paired', dest='is_paired', action='store_true',
                    help='Sample is paired-end reads'),
        make_option('--empty', dest='empty', action='store_true',
                    help='Empty each of the tables'),
        )
        
    @transaction.atomic       
    def handle(self, *args, **options):
        # Required Parameters
        if not options['empty']:
            if not options['experiment']:
                raise CommandError('--experiment is requried')
        else:
            user = User.objects.get(username='public')
            ToSample.objects.all().delete()
            Sample.objects.filter(user=user).delete()
            sys.exit()

        experiment = Experiment.objects.get(pk=options['experiment'])
        try:
            # Experiment already has a sampleid
            ToSample.objects.get(experiment_accession=experiment)
            print '0'
        except ToSample.DoesNotExist:
            # Create new sample
            user = User.objects.get(username='public')
            num_samples = Sample.objects.filter(user_id=user.id).count()
            sample_tag = 'public_{0}'.format(str(num_samples+1).zfill(6))
            
            sample = Sample(
                user=user,
                sample_tag=sample_tag, 
                is_paired=options['is_paired']
            )
            sample.save()
            
            to_sample = ToSample(experiment_accession=experiment, 
                                 sample=sample)
            to_sample.save()
            
            print json.dumps({
                'sample_id':sample.pk, 
                'sample_tag':sample_tag, 
                'username':'public',
            })