"""
update_ena_metadata.

Reads ena related tables and aggregates metadata into a single table.
"""
import sys

from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from ena.models import Study, Experiment, Run, CenterNames
from sample.models import Sample, EnaMetaData


class Command(BaseCommand):
    """Update database with latest ENA publicly available data."""

    help = 'Update database with latest ENA publicly available data.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--empty', action='store_true',
                            help='Empty tables and reset counts.')
        parser.add_argument('--debug', action='store_true',
                            help='Will not write to the database.')

    @transaction.atomic
    def handle(self, *args, **options):
        """Query ENA and retrieve latest results."""
        if options['empty']:
            print("Deleting existing EnaMetaData...")
            EnaMetaData.objects.all().delete()
            sys.exit()

        ena_user = User.objects.get(username='ena')
        ena_samples = Sample.objects.filter(user=ena_user)
        count = 0
        total = ena_samples.count()
        for sample in ena_samples:
            count += 1
            try:
                experiment = Experiment.objects.get(
                    experiment_accession=sample.sample_tag
                )
            except Experiment.DoesNotExist:
                print(
                    "#### {0} NOT FOUND IN DB.####".format(sample.sample_tag)
                )
                continue
            study = Study.objects.get(
                study_accession=experiment.study_accession.pk
            )
            run = Run.objects.filter(
                experiment_accession=sample.sample_tag
            )

            center_name = ''
            center_link = ''
            try:
                center = CenterNames.objects.get(
                    ena_name=experiment.center_name
                )
                center_name = center.name
                center_link = center.link
            except CenterNames.DoesNotExist:
                print("#### {0} center name does not exist. ####".format(
                    experiment.center_name
                ))

            alt_accession = experiment.secondary_sample_accession
            metadata, created = EnaMetaData.objects.update_or_create(
                sample=sample,
                study_accession=study.study_accession,
                study_title=study.study_title,
                study_alias=study.study_alias,
                secondary_study_accession=study.secondary_study_accession,
                sample_accession=experiment.experiment_accession,
                secondary_sample_accession=alt_accession,
                submission_accession=experiment.submission_accession,
                experiment_accession=experiment.experiment_accession,
                experiment_title=experiment.experiment_title,
                experiment_alias=experiment.experiment_alias,
                tax_id=experiment.tax_id,
                scientific_name=experiment.scientific_name,
                instrument_platform=experiment.instrument_platform,
                instrument_model=experiment.instrument_model,
                library_layout=experiment.library_layout,
                library_strategy=experiment.library_strategy,
                library_selection=experiment.library_selection,
                center_name=center_name,
                center_link=center_link,
                first_public=run[0].first_public,
            )
            if created:
                print("{0} of {1} ... {2} ({3})".format(
                    count, total, sample.sample_tag, created
                ))
