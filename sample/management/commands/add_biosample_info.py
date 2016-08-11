"""
add_biosample_info.

Reads output from EBI's data warehouse API and inserts the data into
proper tables.
"""
import time
import urllib2

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from ena.models import Experiment
from sample.models import Sample, MetaData, ToMetaData, Tag, ToTag


class Command(BaseCommand):
    """Update biosample info for a given ENA/SRA experiment."""

    help = 'Update biosample info for a given ENA/SRA experiment.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('sample', metavar='SAMPLE',
                            help=('Sample to check ENA for sample info.'))
        parser.add_argument('--is_project_tag', action='store_true',
                            help=('Update info for all samples associated '
                                  'with a project tag.'))

    def handle(self, *args, **options):
        """Query ENA and retrieve latest results."""
        self.init()

        samples = []
        if options['is_project_tag']:
            samples = self.get_samples_by_project_tag(options['sample'])
        else:
            try:
                sample = Sample.objects.get(pk=options['sample'])
                samples.append(sample)
            except Sample.DoesNotExist as e:
                raise CommandError(
                    'Sample does not exist. {0}'.format(e)
                )

        for sample in samples:
            print("Working on sample: {0} ({1})".format(
                sample.db_tag, sample.sample_tag
            ))
            experiment = self.get_experiment(sample)
            data = self.query_ena(experiment.sample_accession)
            field_values = self.parse_ena(data)
            self.insert(field_values, sample)
            time.sleep(0.5)

    def init(self):
        """Set some global variables."""
        self.fields = [
            'accession', 'secondary_sample_accession', 'collected_by',
            'collection_date', 'country', 'culture_collection', 'description',
            'isolate', 'isolation_source', 'location', 'serotype', 'serovar',
            'strain', 'tax_id', 'scientific_name', 'sample_alias',
            'center_name', 'depth', 'altitude', 'environment_biome',
            'temperature', 'salinity', 'host', 'host_tax_id', 'host_sex',
            'host_body_site', 'ph',
        ]

    def get_samples_by_project_tag(self, tag):
        """Get all samples associated with a project tag."""
        try:
            tag_obj = Tag.objects.get(tag=tag)
        except Tag.DoesNotExist as e:
            raise CommandError('Tag {0} does not exist. {1}'.format(tag, e))

        tag_set = ToTag.objects.filter(tag=tag_obj)
        samples = []
        for row in tag_set:
            samples.append(row.sample)

        return samples

    def get_experiment(self, sample):
        """Return an Experiment object for a given ENA experiment."""
        try:
            return(Experiment.objects.get(
                experiment_accession=sample.sample_tag
            ))
        except Experiment.DoesNotExist as e:
            raise CommandError(
                'Experiment {0} does not exist. {1}'.format(
                    sample.sample_tag, e
                )
            )

    def query_ena(self, accession):
        """USE ENA's API to retreieve the latest results."""
        # ENA browser info: http://www.ebi.ac.uk/ena/about/browser
        address = 'http://www.ebi.ac.uk/ena/data/warehouse/search'
        query = urllib2.quote('accession="{0}"'.format(accession))
        domain = 'domain=sample'
        result = 'result=sample'
        display = 'display=report'

        url = '{0}?query={1}&{2}&{3}&{4}&fields={5}'.format(
            address, query, domain, result, display, ','.join(self.fields)
        )

        f = urllib2.urlopen(url)
        data = f.readlines()
        f.close()

        if len(data) <= 1:
            raise CommandError('No results were returned from ENA.')

        return data

    def parse_ena(self, data):
        """Parse the retrieved ENA data."""
        for line in data:
            line = line.rstrip()
            if line.startswith(self.fields[0]) or not line:
                continue
            else:
                col_vals = line.split('\t')
                return dict(zip(self.fields, col_vals))

    @transaction.atomic
    def get_metadata_field(self, field):
        if field == 'accession':
            field = 'sample_accession'

        created = False
        try:
            metadata_obj = MetaData.objects.get(field=field)
        except MetaData.DoesNotExist:
            metadata_obj = MetaData.objects.create(
                field=field, description="NONE GIVEN"
            )
            created = True

        if created:
            print("Added new field: {0}".format(field))

        return metadata_obj

    @transaction.atomic
    def insert(self, data, sample):
        """Insert experiment results to the database."""
        for field, value in data.items():
            if value:
                metadata_obj = self.get_metadata_field(field)
                obj, created = ToMetaData.objects.get_or_create(
                    sample=sample,
                    metadata=metadata_obj,
                    value=value
                )
                print("{0}\t{1}\t{2}\t{3}".format(
                    sample.sample_tag, field, value, created
                ))
            else:
                print("{0}\t{1}\t{2}\tSkipped field with empty value".format(
                    sample.sample_tag, field, value
                ))
