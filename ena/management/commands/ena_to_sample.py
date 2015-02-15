""" Create a new Sample for an ENA experiement. """
import sys
import json

from optparse import make_option

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from ena.models import Experiment, ToSample, Run
from samples.models import Sample


class Command(BaseCommand):

    """ Create new sample for ENA data. """

    help = 'Return the paired status of an experiment accession'

    option_list = BaseCommand.option_list + (
        make_option('--experiment', dest='experiment',
                    help='Experiment accession for ENA entry.'),
        make_option('--empty', dest='empty', action='store_true',
                    help='Empty each of the tables'),
    )

    @transaction.atomic
    def handle(self, *args, **options):
        """ Create new sample for ENA data. """
        # Required Parameters
        if not options['empty']:
            if not options['experiment']:
                raise CommandError('--experiment is requried')
        else:
            user = User.objects.get(username='ena')
            ToSample.objects.all().delete()
            Sample.objects.filter(user=user).delete()
            sys.exit()

        experiment = Experiment.objects.get(pk=options['experiment'])
        run = Run.objects.filter(experiment_accession=experiment)[:1].get()
        try:
            # Experiment already has a sampleid
            to_sample = ToSample.objects.get(experiment_accession=experiment)
            Sample.objects.filter(pk=to_sample.sample.pk).update(
                is_paired=run.is_paired,
                sequencing_center=experiment.center_name,
                sequencing_platform=experiment.instrument_model,
                strain=experiment.scientific_name,
                comments=(
                    'Experiment Title: {0}\n'
                    'Experiment Alias: {1}\n'
                    'Taxonomy ID: {2}\n'
                    'Study Accession: {3}\n'
                    'Sample Accession: {4}, {5}\n'
                    'Submission Accession: {6}\n'
                ).format(
                    experiment.experiment_title,
                    experiment.experiment_alias,
                    experiment.tax_id,
                    experiment.study_accession.study_accession,
                    experiment.sample_accession,
                    experiment.secondary_sample_accession,
                    experiment.submission_accession
                )
            )
            print json.dumps({
                'sample_id': to_sample.sample.pk,
                'sample_tag': options['experiment'],
                'username': 'ena',
            })
        except ToSample.DoesNotExist:
            # Create new sample
            user = User.objects.get(username='ena')
            sample_tag = options['experiment']

            sample = Sample(
                user=user,
                sample_tag=sample_tag,
                is_paired=run.is_paired,
                sequencing_center=experiment.center_name,
                sequencing_platform=experiment.instrument_model,
                strain=experiment.scientific_name,
                comments=(
                    'Experiment Title: {0}\n'
                    'Experiment Alias: {1}\n'
                    'Taxonomy ID: {2}\n'
                    'Study Accession: {3}\n'
                    'Sample Accession: {4}, {5}\n'
                    'Submission Accession: {6}\n'
                ).format(
                    experiment.experiment_title,
                    experiment.experiment_alias,
                    experiment.tax_id,
                    experiment.study_accession.study_accession,
                    experiment.sample_accession,
                    experiment.secondary_sample_accession,
                    experiment.submission_accession
                )
            )
            sample.save()

            to_sample = ToSample(experiment_accession=experiment,
                                 sample=sample)
            to_sample.save()

            print json.dumps({
                'sample_id': sample.pk,
                'sample_tag': sample_tag,
                'username': 'ena',
            })
