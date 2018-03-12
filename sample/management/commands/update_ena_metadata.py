"""
update_ena_metadata.

Reads ena related tables and aggregates metadata into a single table.
"""
import sys

from django.db import connection, transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from ena.models import Study, Experiment, Run, CenterNames, BioSample
from sample.models import Sample, Metadata, MetadataFields


class Command(BaseCommand):
    """Update database with latest ENA publicly available data."""

    help = 'Update database with latest ENA publicly available data.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('locations',
                            help=('Tab-delimted text file containing '
                                  'corrected locations.'))
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

        fields = [
            'contains_ena_metadata', 'study_accession', 'study_title',
            'study_alias', 'secondary_study_accession', 'sample_accession',
            'secondary_sample_accession', 'submission_accession',
            'experiment_accession', 'experiment_title', 'experiment_alias',
            'tax_id', 'scientific_name', 'instrument_platform',
            'instrument_model', 'library_layout', 'library_strategy',
            'library_selection', 'center_name', 'center_link', 'first_public',
            'cell_line', 'collected_by', 'collection_date', 'location',
            'country', 'region', 'description', 'environmental_sample',
            'biosample_first_public', 'germline', 'isolate',
            'isolation_source', 'coordinates', 'serotype', 'serovar', 'sex',
            'submitted_sex', 'strain', 'sub_species', 'tissue_type',
            'biosample_tax_id', 'biosample_scientific_name', 'sample_alias',
            'checklist', 'biosample_center_name', 'environment_biome',
            'environment_feature', 'environment_material', 'project_name',
            'host', 'host_tax_id', 'host_status', 'host_sex',
            'submitted_host_sex', 'host_body_site', 'investigation_type',
            'sequencing_method', 'broker_name', 'is_public', 'is_published'
        ]

        # Add the fields to the database
        for field in fields:
            MetadataFields.objects.get_or_create(field=field)

        self.locations = {}
        with open(options['locations'], 'r') as fh:
            for line in fh:
                cols = line.rstrip().split('\t')
                location = cols[0]
                self.locations[location] = {'country': "unknown/missing",
                                            'region': "unknown/missing"}
                if len(cols) >= 2:
                    self.locations[location]['country'] = cols[1]
                if len(cols) == 3:
                    self.locations[location]['region'] = cols[2]

        ena_user = User.objects.get(username='ena')
        ena_samples = Sample.objects.filter(user=ena_user)
        count = 0
        for sample in ena_samples:
            metadata = {}
            count += 1
            try:
                exp = Experiment.objects.get(
                    experiment_accession=sample.name
                )
            except Experiment.DoesNotExist:
                print(
                    "#### {0} NOT FOUND IN DB.####".format(sample.name)
                )
                continue
            study = Study.objects.get(
                study_accession=exp.study_accession.pk
            )
            run = Run.objects.filter(
                experiment_accession=sample.name
            )

            center_name = exp.center_name
            center_link = ''
            try:
                center = CenterNames.objects.get(
                    ena_name=exp.center_name
                )
                center_name = center.name
                center_link = center.link
            except CenterNames.DoesNotExist:
                if exp.center_name:
                    print("#### {0} center name does not exist. ####".format(
                        exp.center_name
                    ))

            try:
                bs = BioSample.objects.get(
                    accession=exp.sample_accession
                )
            except BioSample.DoesNotExist:
                print("BioSample: {0} ({1}) not found... Skipping".format(
                    exp.sample_accession,
                    exp.experiment_accession
                ))
                bs = None

            alt_accession = exp.secondary_sample_accession
            if bs:
                location = bs.country
                country = "unknown/missing"
                region = "unknown/missing"
                if bs.country in self.locations:
                    country = self.locations[location]['country']
                    region = self.locations[location]['region']
                else:
                    location = "unknown/missing"
                secondary_study_accession = study.secondary_study_accession

                metadata = {
                    'contains_ena_metadata': True,
                    'study_accession': study.study_accession,
                    'study_title': study.study_title,
                    'study_alias': study.study_alias,
                    'secondary_study_accession': secondary_study_accession,
                    'sample_accession': exp.sample_accession,
                    'secondary_sample_accession': alt_accession,
                    'submission_accession': exp.submission_accession,
                    'experiment_accession': exp.experiment_accession,
                    'experiment_title': exp.experiment_title,
                    'experiment_alias': exp.experiment_alias,
                    'tax_id': exp.tax_id,
                    'scientific_name': exp.scientific_name,
                    'instrument_platform': exp.instrument_platform,
                    'instrument_model': exp.instrument_model,
                    'library_layout': exp.library_layout,
                    'library_strategy': exp.library_strategy,
                    'library_selection': exp.library_selection,
                    'center_name': center_name,
                    'center_link': center_link,
                    'first_public': run[0].first_public,

                    # BioSample fields
                    'cell_line': bs.cell_line,
                    'collected_by': bs.collected_by,
                    'collection_date': bs.collection_date,
                    'location': location,
                    'country': country,
                    'region': region,
                    'description': bs.description,
                    'environmental_sample': bs.environmental_sample,
                    'biosample_first_public': bs.first_public,
                    'germline': bs.germline,
                    'isolate': bs.isolate,
                    'isolation_source': bs.isolation_source,
                    'coordinates': bs.location,
                    'serotype': bs.serotype,
                    'serovar': bs.serovar,
                    'sex': bs.sex,
                    'submitted_sex': bs.submitted_sex,
                    'strain': bs.strain,
                    'sub_species': bs.sub_species,
                    'tissue_type': bs.tissue_type,
                    'biosample_tax_id': bs.tax_id,
                    'biosample_scientific_name': bs.scientific_name,
                    'sample_alias': bs.sample_alias,
                    'checklist': bs.checklist,
                    'biosample_center_name': bs.center_name,
                    'environment_biome': bs.environment_biome,
                    'environment_feature': bs.environment_feature,
                    'environment_material': bs.environment_material,
                    'project_name': bs.project_name,
                    'host': bs.host,
                    'host_tax_id': bs.host_tax_id,
                    'host_status': bs.host_status,
                    'host_sex': bs.host_sex,
                    'submitted_host_sex': bs.submitted_host_sex,
                    'host_body_site': bs.host_body_site,
                    'investigation_type': bs.investigation_type,
                    'sequencing_method': bs.sequencing_method,
                    'broker_name': bs.broker_name,
                    'is_public': sample.is_public,
                    'is_published': sample.is_published
                }
            else:
                metadata = {
                    'contains_ena_metadata': True,
                    'study_accession': study.study_accession,
                    'study_title': study.study_title,
                    'study_alias': study.study_alias,
                    'secondary_study_accession': secondary_study_accession,
                    'sample_accession': exp.sample_accession,
                    'secondary_sample_accession': alt_accession,
                    'submission_accession': exp.submission_accession,
                    'experiment_accession': exp.experiment_accession,
                    'experiment_title': exp.experiment_title,
                    'experiment_alias': exp.experiment_alias,
                    'tax_id': exp.tax_id,
                    'scientific_name': exp.scientific_name,
                    'instrument_platform': exp.instrument_platform,
                    'instrument_model': exp.instrument_model,
                    'library_layout': exp.library_layout,
                    'library_strategy': exp.library_strategy,
                    'library_selection': exp.library_selection,
                    'center_name': center_name,
                    'center_link': center_link,
                    'first_public': run[0].first_public,
                    'is_public': sample.is_public,
                    'is_published': sample.is_published
                }

            cleaned_up = {}
            for key, val in metadata.items():
                if val:
                    cleaned_up[key] = val

            try:
                Metadata.objects.create(
                    sample=sample,
                    metadata=cleaned_up,
                    history={}
                )
            except IntegrityError as e:
                raise CommandError(' '.join([
                    f'Metadata Error: {sample.name} ({sample.id}).',
                    f'Please use --force to update stats. Error: {e}'
                ]))

    def empty_table(self, table):
        """Empty Table and Reset id counters to 1."""
        print("Emptying {0}...".format(table))
        query = "DELETE FROM {0} WHERE contains_ena_metadata=TRUE;".format(
            table
        )
        cursor = connection.cursor()
        cursor.execute(query)
