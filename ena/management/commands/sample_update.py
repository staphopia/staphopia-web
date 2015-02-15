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

    help = 'Update ENA experiments in Sample table.'

    option_list = BaseCommand.option_list + (
        make_option('--experiment', dest='experiment',
                    help='Experiment accession for ENA entry.'),
    )

    @transaction.atomic
    def handle(self, *args, **options):
        """ Create new sample for ENA data. """
        # Required Parameters

        experiment = Experiment.objects.get(pk=options['experiment'])
        try:
            # Experiment already has a sampleid
            to_sample = ToSample.objects.get(experiment_accession=experiment)
        except ToSample.DoesNotExist:
            raise CommandError('This epriment is not in Smaple table.')

        run = Run.objects.filter(experiment_accession=experiment)[:1].get()
        Sample.objects.filter(pk=to_sample.sample.pk).update(
            is_paired=run.is_paired,
            sequencing_center=experiment.center_name,
            sequencing_platform=experiment.instrument_model,
            strain=experiment.scientific_name,
            comments=(
                'Experiment Title: {0}\n'
                'Experiment Alias: {1}\n'
                'Taxonomy ID: {2}'
                'Study Accession: {3}'
                'Sample Accession: {4}, {5}'
                'Submission Accession: {6}'
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
