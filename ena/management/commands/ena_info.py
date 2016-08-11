"""Outputs Experiments and corresponding runs information in JSON format."""
import json
from django.core.management.base import BaseCommand

from ena.models import Experiment, Run


class Command(BaseCommand):

    """ . """

    help = 'Output ENA info in JSON format.'

    def add_arguments(self, parser):
        parser.add_argument('--study', dest='study',
                            help='Filter runs based on study accession.')
        parser.add_argument('--experiment', dest='experiment',
                            help='Filter runs  based on experiment accession.')
        parser.add_argument('--run', dest='run',
                            help='Filter runs based on run accession.')


    def handle(self, *args, **opts):
        hits = None
        if opts['experiment']:
            hits = self.get_experiments(opts['experiment'],
                                               is_experiment=True)
        elif opts['study']:
            hits = self.get_experiments(opts['study'])
        elif opts['run']:
            hits = self.get_runs(opts['run'], is_run=True)

        if hits:
            run_info = {}
            for hit in hits:
                if opts['run']:
                    exp = hit.experiment_accession.experiment_accession
                    run_info[exp] = {}
                    run_info[exp][hit.run_accession] = hit.is_paired
                else:
                    exp = hit.experiment_accession
                    run_info[exp] = {}
                    runs = self.get_runs(exp)
                    if runs.count() > 0:
                        for run in runs:
                            run_info[exp][run.run_accession] = {
                                'is_paired': run.is_paired,
                                'fastq_ftp': run.fastq_ftp.split(';'),
                                'fastq_aspera': run.fastq_aspera.split(';'),
                                'fastq_md5': run.fastq_md5.split(';')
                            }

            print json.dumps(run_info)


    def get_experiments(self, accession, is_experiment=False):
        if is_experiment:
            return Experiment.objects.filter(experiment_accession=accession)
        else:
            return Experiment.objects.filter(study_accession=accession)


    def get_runs(self, accession, is_run=False):

        if is_run:
            return Run.objects.filter(run_accession=accession)
        else:
            return Run.objects.filter(experiment_accession=accession)
