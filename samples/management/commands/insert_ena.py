'''

'''
import os.path
from optparse import make_option

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from samples.models.ena import *

class Command(BaseCommand):
    help = 'Insert ENA data information into the database.'

    option_list = BaseCommand.option_list + (
        make_option('--study', dest='study',
                    help='A table of study information.'),
        make_option('--experiment', dest='experiment',
                    help='A table of experiment information.'),
        make_option('--run', dest='run',
                    help='A table of run information'),
        make_option('--debug', action='store_true', dest='debug', 
                    default=False, help='Will not write to the database'),
        )
        
    def handle(self, *args, **options):
        # Required Parameters
        if not options['study']:
            raise CommandError('--study is requried')
        elif not options['experiment']:
            raise CommandError('--experiment is requried')
        elif not options['run']:
            raise CommandError('--run is requried')

        # Test input files
        if not os.path.exists(options['study']):
            raise CommandError('{0} does not exist'.format(options['study']))
        elif not os.path.exists(options['experiment']):
            raise CommandError('{0} does not exist'.format(options['experiment']))
        elif not os.path.exists(options['run']):
            raise CommandError('{0} does not exist'.format(options['run']))
            
        # Insert Studies
        studies_created = self.insert_studies(options['study'])
        
        # Insert Experiments
        exps_created = self.insert_experiments(options['experiment'])
        
        # Insert Runs
        runs_created = self.insert_runs(options['run'])
        
        print 'New Studies: {0}\nNew Experiments: {1}\nNew Runs: {2}'.format(
            studies_created, exps_created, runs_created
        )

        
    @transaction.atomic    
    def insert_studies(self, input_file):
        '''
        
        '''
        count = 0
        col_names = False
        fh = open(input_file, 'r')
        for line in fh:
            col_vals = line.rstrip().split('\t')
            if not col_names:
                col_names = col_vals
            else:
                cols = dict(zip(col_names, col_vals))
                
                # Test if study exists, if not create
                try:
                    study = EnaStudy.objects.get(
                        study_accession=cols['study_accession']
                    )
                except EnaStudy.DoesNotExist:
                    study = EnaStudy(**cols)
                    study.save()
                    count += 1 
        fh.close()
        
        return count

    @transaction.atomic  
    def insert_experiments(self, input_file):
        '''
        
        '''
        count = 0
        col_names = False
        fh = open(input_file, 'r')
        for line in fh:
            col_vals = line.rstrip().split('\t')
            if not col_names:
                col_names = col_vals
            else:
                cols = dict(zip(col_names, col_vals))
                
                # Study 
                try:
                    cols['study_accession'] = EnaStudy.objects.get(
                        pk=cols['study_accession']
                    )
                except EnaStudy.DoesNotExist:
                    raise CommandError('Please Check: {0} '.format(
                        options['experiment_accession'])
                    )
                
                # Test if experiment exists, if not create
                try:
                    exp = EnaExperiment.objects.get(
                        experiment_accession=cols['experiment_accession']
                    )
                except EnaExperiment.DoesNotExist:
                    exp = EnaExperiment(**cols)
                    exp.save()
                    count += 1 
        fh.close()
        
        return count
    
    @transaction.atomic  
    def insert_runs(self, input_file):
        '''
        
        '''
        count = 0
        col_names = False
        fh = open(input_file, 'r')
        for line in fh:
            col_vals = line.rstrip().split('\t')
            if not col_names:
                col_names = col_vals
            else:
                cols = dict(zip(col_names, col_vals))
                
                # Experiment 
                try:  
                    cols['experiment_accession'] = EnaExperiment.objects.get(
                        pk=cols['experiment_accession']
                    )
                except EnaExperiment.DoesNotExist:
                    raise CommandError('Please Check: {0} '.format(
                        options['run_accession'])
                    )
                
                # Test if run exists, if not create
                try:
                    run = EnaRun.objects.get(
                        run_accession=cols['run_accession']
                    )
                except EnaRun.DoesNotExist:
                    run = EnaRun(**cols)
                    run.save()
                    count += 1 
        fh.close()
        
        return count