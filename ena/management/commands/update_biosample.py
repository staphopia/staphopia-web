"""
update_biosample.

Reads output from EBI's data warehouse API and inserts the data into
proper tables.
"""
import sys
import requests

from django.core.mail import EmailMessage
from django.db import transaction, Error
from django.core.management.base import BaseCommand, CommandError

from ena.models import BioSample


class Command(BaseCommand):
    """Update database with latest ENA publicly available data."""

    help = 'Update database with latest ENA publicly available data.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--empty', action='store_true',
                            help='Empty tables and reset counts.')
        parser.add_argument('--debug', action='store_true',
                            help='Will not write to the database.')

    def handle(self, *args, **options):
        """Query ENA and retrieve latest results."""
        if options['empty']:
            BioSample.objects.all().delete()
            sys.exit()
        else:
            self.init()
            data = self.query_ena()
            self.parse_ena(data)

            if not options['debug']:
                # Insert results to the database
                self.samples_created = self.insert(self.ena_samples, BioSample)
            else:
                print("Debug option given, skipping database insert.")

            self.print_stats()
            self.email_stats()

    def init(self):
        """Set some global variables."""
        self.genome_size = 2878897
        self.samples_created = 0
        self.missing = 0
        self.ena_samples = {}
        self.fields = [
            'accession', 'bio_material', 'target_gene', 'ph', 'broker_name',
            'cell_line', 'cell_type', 'collected_by', 'collection_date',
            'country', 'cultivar', 'culture_collection', 'description',
            'dev_stage', 'ecotype', 'environmental_sample', 'first_public',
            'germline', 'identified_by', 'isolate', 'isolation_source',
            'location', 'mating_type', 'serotype', 'serovar', 'sex',
            'submitted_sex', 'specimen_voucher', 'strain', 'sub_species',
            'sub_strain', 'tissue_lib', 'tissue_type', 'variety', 'tax_id',
            'scientific_name', 'sample_alias', 'checklist', 'center_name',
            'depth', 'elevation', 'altitude', 'environment_biome',
            'environment_feature', 'environment_material', 'temperature',
            'salinity', 'sampling_campaign', 'sampling_site',
            'sampling_platform', 'protocol_label', 'project_name', 'host',
            'host_tax_id', 'host_status', 'host_sex', 'submitted_host_sex',
            'host_body_site', 'host_gravidity', 'host_phenotype',
            'host_genotype', 'host_growth_conditions', 'environmental_package',
            'investigation_type', 'experimental_factor', 'sample_collection',
            'sequencing_method', 'secondary_sample_accession',
        ]
        self.counts = {}
        for field in self.fields:
            self.counts[field] = 0

    def query_ena(self):
        """USE ENA's API to retreieve the latest results."""
        # ENA browser info: http://www.ebi.ac.uk/ena/about/browser
        address = 'http://www.ebi.ac.uk/ena/data/warehouse/search'
        query = "tax_tree(1280)"
        result = 'result=sample'
        display = 'display=report'
        limit = 'limit=1000000'

        url = '{0}?query={1}&{2}&{3}&{4}&fields={5}'.format(
            address, query, result, display, limit, ','.join(self.fields)
        )

        response = requests.get(url)

        if len(response.text) <= 1:
            raise CommandError('No results were returned from ENA.')

        return response.text.split('\n')

    def parse_ena(self, data):
        """Parse the retrieved ENA data."""
        for line in data:
            line = line.rstrip()
            if line.startswith(self.fields[0]):
                continue
            else:
                col_vals = line.split('\t')
                if len(col_vals) == 68:
                    c = dict(zip(self.fields, col_vals))
                    for key, value in c.items():
                        if value:
                            self.counts[key] += 1

                    self.ena_samples[c['accession']] = {
                        'accession': c['accession'],
                        'secondary_sample_accession': c['secondary_sample_accession'],
                        'bio_material': c['bio_material'],
                        'cell_line': c['cell_line'],
                        'cell_type': c['cell_type'],
                        'collected_by': c['collected_by'],
                        'collection_date': c['collection_date'],
                        'country': c['country'],
                        'cultivar': c['cultivar'],
                        'culture_collection': c['culture_collection'],
                        'description': c['description'],
                        'dev_stage': c['dev_stage'],
                        'ecotype': c['ecotype'],
                        'environmental_sample': c['environmental_sample'],
                        'first_public': c['first_public'],
                        'germline': c['germline'],
                        'identified_by': c['identified_by'],
                        'isolate': c['isolate'],
                        'isolation_source': c['isolation_source'],
                        'location': c['location'],
                        'mating_type': c['mating_type'],
                        'serotype': c['serotype'],
                        'serovar': c['serovar'],
                        'sex': c['sex'],
                        'submitted_sex': c['submitted_sex'],
                        'specimen_voucher': c['specimen_voucher'],
                        'strain': c['strain'],
                        'sub_species': c['sub_species'],
                        'sub_strain': c['sub_strain'],
                        'tissue_lib': c['tissue_lib'],
                        'tissue_type': c['tissue_type'],
                        'variety': c['variety'],
                        'tax_id': c['tax_id'],
                        'scientific_name': c['scientific_name'],
                        'sample_alias': c['sample_alias'],
                        'checklist': c['checklist'],
                        'center_name': c['center_name'],
                        'depth': c['depth'],
                        'elevation': c['elevation'],
                        'altitude': c['altitude'],
                        'environment_biome': c['environment_biome'],
                        'environment_feature': c['environment_feature'],
                        'environment_material': c['environment_material'],
                        'temperature': c['temperature'],
                        'salinity': c['salinity'],
                        'sampling_campaign': c['sampling_campaign'],
                        'sampling_site': c['sampling_site'],
                        'sampling_platform': c['sampling_platform'],
                        'protocol_label': c['protocol_label'],
                        'project_name': c['project_name'],
                        'host': c['host'],
                        'host_tax_id': c['host_tax_id'],
                        'host_status': c['host_status'],
                        'host_sex': c['host_sex'],
                        'submitted_host_sex': c['submitted_host_sex'],
                        'host_body_site': c['host_body_site'],
                        'host_gravidity': c['host_gravidity'],
                        'host_phenotype': c['host_phenotype'],
                        'host_genotype': c['host_genotype'],
                        'host_growth_conditions': c['host_growth_conditions'],
                        'environmental_package': c['environmental_package'],
                        'investigation_type': c['investigation_type'],
                        'experimental_factor': c['experimental_factor'],
                        'sample_collection': c['sample_collection'],
                        'sequencing_method': c['sequencing_method'],
                        'target_gene': c['target_gene'],
                        'ph': c['ph'],
                        'broker_name': c['broker_name']
                    }
                else:
                    self.missing += 1

    @transaction.atomic
    def insert(self, ena_data, ena_obj):
        """Insert experiment results to the database."""
        total_created = 0
        for key, row in ena_data.items():
            try:
                data = {}
                for k, v in row.items():
                    if k not in ['accession', 'secondary_sample_accession']:
                        data[k] = v
                obj, created = ena_obj.objects.update_or_create(
                    accession=row['accession'],
                    secondary_sample_accession=row['secondary_sample_accession'],
                    defaults=data
                )
                if created:
                    total_created += 1
            except Error as e:
                raise CommandError(e)
        return total_created

    def print_stats(self):
        """Print some final results."""
        print('ENA Data Summary (new additions in parentheses)')
        print('Samples: {0} ({1})'.format(
            len(self.ena_samples),
            self.samples_created
        ))
        for key, val in self.counts.items():
            print("{0}\t{1}".format(key, val))

    def email_stats(self):
        """Email admin with update."""
        field_counts = []
        for key, val in self.counts.items():
            field_counts.append("{0}\t{1}\n".format(key, val))
        labrat = "Staphopia's Friendly Robot <usa300@staphopia.com>"
        subject = '[Staphopia ENA Update] - BioSample info has been updated.'
        message = (
            "Project information from ENA has been updated.\n\n"
            "New ENA BioSample Additions (total in parentheses)\n"
            "Samples: {0} ({1})\n\n"
            "Data Per Field\n"
            "{2}"
        ).format(
            self.samples_created,
            len(self.ena_samples),
            "".join(field_counts)
        )
        recipients = ['admin@staphopia.com', 'robert.petit@emory.edu']
        email = EmailMessage(subject, message, labrat, recipients)
        email.send(fail_silently=False)
