"""
update_ena_metadata.

Reads ena related tables and aggregates metadata into a single table.
"""
import sys

from django.db import connection, transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from ena.models import Study, Experiment, Run, CenterNames, BioSample
from sample.models import Sample, MetaData


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
            self.empty_table('sample_metadata')
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

            center_name = experiment.center_name
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

            try:
                bs = BioSample.objects.get(
                    accession=experiment.sample_accession
                )
            except BioSample.DoesNotExist:
                print("BioSample: {0} ({1}) not found... Skipping".format(
                    experiment.sample_accession,
                    experiment.experiment_accession
                ))
                bs = None

            alt_accession = experiment.secondary_sample_accession
            if bs:
                metadata, created = MetaData.objects.update_or_create(
                    sample=sample,
                    contains_ena_metadata=True,
                    study_accession=study.study_accession,
                    study_title=study.study_title,
                    study_alias=study.study_alias,
                    secondary_study_accession=study.secondary_study_accession,
                    sample_accession=experiment.sample_accession,
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

                    # BioSample fields
                    cell_line=bs.cell_line,
                    collected_by=bs.collected_by,
                    collection_date=bs.collection_date,
                    country=bs.country,
                    description=bs.description,
                    environmental_sample=bs.environmental_sample,
                    biosample_first_public=bs.first_public,
                    germline=bs.germline,
                    isolate=bs.isolate,
                    isolation_source=bs.isolation_source,
                    location=bs.location,
                    serotype=bs.serotype,
                    serovar=bs.serovar,
                    sex=bs.sex,
                    submitted_sex=bs.submitted_sex,
                    strain=bs.strain,
                    sub_species=bs.sub_species,
                    tissue_type=bs.tissue_type,
                    biosample_tax_id=bs.tax_id,
                    biosample_scientific_name=bs.scientific_name,
                    sample_alias=bs.sample_alias,
                    checklist=bs.checklist,
                    biosample_center_name=bs.center_name,
                    environment_biome=bs.environment_biome,
                    environment_feature=bs.environment_feature,
                    environment_material=bs.environment_material,
                    project_name=bs.project_name,
                    host=bs.host,
                    host_tax_id=bs.host_tax_id,
                    host_status=bs.host_status,
                    host_sex=bs.host_sex,
                    submitted_host_sex=bs.submitted_host_sex,
                    host_body_site=bs.host_body_site,
                    investigation_type=bs.investigation_type,
                    sequencing_method=bs.sequencing_method,
                    broker_name=bs.broker_name
                )
            else:
                metadata, created = MetaData.objects.update_or_create(
                    sample=sample,
                    contains_ena_metadata=True,
                    study_accession=study.study_accession,
                    study_title=study.study_title,
                    study_alias=study.study_alias,
                    secondary_study_accession=study.secondary_study_accession,
                    sample_accession=experiment.sample_accession,
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
                    first_public=run[0].first_public
                )
            """if created:
                print("{0} of {1} ... {2} ({3})".format(
                    count, total, sample.sample_tag, created
                ))
            """

    def empty_table(self, table):
        """Empty Table and Reset id counters to 1."""
        print("Emptying {0}...".format(table))
        query = "DELETE FROM {0} WHERE contains_ena_metadata=TRUE;".format(
            table
        )
        cursor = connection.cursor()
        cursor.execute(query)
