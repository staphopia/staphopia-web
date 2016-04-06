"""
update_ena.

Reads output from EBI's data warehouse API and inserts the data into
proper tables.
"""
import sys
import urllib2

from django.core.mail import EmailMessage
from django.db import transaction, Error
from django.core.management.base import BaseCommand, CommandError

from ena.models import Study, Experiment, Run


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
            Study.objects.all().delete()
            Experiment.objects.all().delete()
            Run.objects.all().delete()
            sys.exit()
        else:
            self.init()
            data = self.query_ena()
            self.parse_ena(data)

            if not options['debug']:
                # Insert results to the database
                self.studies_created = self.insert(self.ena_studies, Study)
                self.exps_created = self.insert(self.ena_exps, Experiment)
                self.runs_created = self.insert(self.ena_runs, Run)
            else:
                print("Debug option given, skipping database insert.")

            self.print_stats()
            self.email_stats()

    def init(self):
        """Set some global variables."""
        self.genome_size = 2878897
        self.fields = [
            'study_accession', 'sample_accession', 'experiment_accession',
            'run_accession', 'submission_accession', 'tax_id',
            'scientific_name', 'instrument_platform', 'instrument_model',
            'library_layout', 'library_strategy', 'library_selection',
            'read_count', 'base_count', 'center_name', 'first_public',
            'fastq_bytes', 'fastq_md5', 'fastq_aspera', 'fastq_ftp',
            'run_alias', 'study_title', 'secondary_study_accession',
            'secondary_sample_accession', 'experiment_title', 'study_alias',
            'experiment_alias'
        ]

        self.studies_created = 0
        self.ena_studies = {}
        self.study_fields = ['study_accession', 'secondary_study_accession',
                             'study_title', 'study_alias']

        self.exps_created = 0
        self.ena_exps = {}
        self.exp_fields = [
            'experiment_accession', 'experiment_title', 'experiment_alias',
            'study_accession', 'sample_accession',
            'secondary_sample_accession', 'submission_accession', 'tax_id',
            'scientific_name', 'instrument_platform', 'instrument_model',
            'library_layout', 'library_strategy', 'library_selection',
            'center_name'
        ]

        self.runs_created = 0
        self.ena_runs = {}
        self.run_fields = [
            'run_accession', 'experiment_accession', 'is_paired', 'run_alias',
            'read_count', 'base_count', 'mean_read_length', 'coverage',
            'first_public', 'fastq_bytes', 'fastq_md5', 'fastq_aspera',
            'fastq_ftp'
        ]
        self.missing = 0

    def query_ena(self):
        """USE ENA's API to retreieve the latest results."""
        # ENA browser info: http://www.ebi.ac.uk/ena/about/browser
        address = 'http://www.ebi.ac.uk/ena/data/warehouse/search'
        query = urllib2.quote((
            '"tax_tree(1280) AND library_source=GENOMIC AND '
            '(library_strategy=OTHER OR library_strategy=WGS OR '
            'library_strategy=WGA) AND (library_selection=MNase OR '
            'library_selection=RANDOM OR library_selection=unspecified OR '
            'library_selection="size fractionation")"'
        ))
        result = 'result=read_run'
        display = 'display=report'
        limit = 'limit=1000000'

        url = '{0}?query={1}&{2}&{3}&{4}&fields={5}'.format(
            address, query, result, display, limit, ','.join(self.fields)
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
            if line.startswith(self.fields[0]):
                continue
            else:
                col_vals = line.split('\t')
                if len(col_vals) == 27:
                    c = dict(zip(self.fields, col_vals))
                    mean_read_length = 0
                    coverage = 0
                    try:
                        mean_read_length = (
                            float(c['base_count']) / float(c['read_count'])
                        )
                        coverage = float(c['base_count']) / self.genome_size
                    except:
                        continue

                    if c['study_accession'] not in self.ena_studies:
                        self.ena_studies[c['study_accession']] = {
                            'study_accession': c['study_accession'],
                            'secondary_study_accession': (
                                c['secondary_study_accession']
                            ),
                            'study_title': ' '.join(c['study_title'].split()),
                            'study_alias': c['study_alias'],
                        }

                    if c['experiment_accession'] not in self.ena_exps:
                        self.ena_exps[c['experiment_accession']] = {
                            'experiment_accession': c['experiment_accession'],
                            'experiment_title': (
                                ' '.join(c['experiment_title'].split())
                            ),
                            'experiment_alias': c['experiment_alias'],
                            'study_accession': Study(
                                study_accession=c['study_accession']
                            ),
                            'sample_accession': c['sample_accession'],
                            'secondary_sample_accession': (
                                c['secondary_sample_accession']
                            ),
                            'submission_accession': c['submission_accession'],
                            'tax_id': c['tax_id'],
                            'scientific_name': c['scientific_name'],
                            'instrument_platform': c['instrument_platform'],
                            'instrument_model': c['instrument_model'],
                            'library_layout': c['library_layout'],
                            'library_strategy': c['library_strategy'],
                            'library_selection': c['library_selection'],
                            'center_name': c['center_name'],
                        }

                    if c['run_accession'] not in self.ena_runs:
                        self.ena_runs[c['run_accession']] = {
                            'experiment_accession': Experiment(
                                experiment_accession=c['experiment_accession']
                            ),
                            'is_paired': (
                                '1' if c['library_layout'] == 'PAIRED' else '0'
                            ),
                            'run_accession': c['run_accession'],
                            'run_alias': c['run_alias'],
                            'read_count': c['read_count'],
                            'base_count': c['base_count'],
                            'mean_read_length': '{0:.2f}'.format(
                                mean_read_length
                            ),
                            'coverage': '{0:.2f}'.format(coverage),
                            'first_public': c['first_public'],
                            'fastq_bytes': c['fastq_bytes'],
                            'fastq_md5': c['fastq_md5'],
                            'fastq_aspera': c['fastq_aspera'],
                            'fastq_ftp': c['fastq_ftp'],
                        }
                else:
                    self.missing += 1

    @transaction.atomic
    def insert(self, ena_data, ena_obj):
        """Insert experiment results to the database."""
        total_created = 0
        for key, row in ena_data.items():
            try:
                obj, created = ena_obj.objects.update_or_create(
                    defaults=row, **row
                )
                if created:
                    total_created += 1
            except Error as e:
                raise CommandError(e)
        return total_created

    def print_stats(self):
        """Print some final results."""
        print('ENA Data Summary (new additions in parentheses)')
        print('Studies: {0} ({1})'.format(
            len(self.ena_studies),
            self.studies_created
        ))
        print('Experiments: {0} ({1})'.format(
            len(self.ena_exps),
            self.exps_created
        ))
        print('Runs: {0} ({1})'.format(
            len(self.ena_runs),
            self.runs_created
        ))

    def email_stats(self):
        """Email admin with update."""
        labrat = "Staphopia's Friendly Robot <usa300@staphopia.com>"
        subject = '[Staphopia ENA Update] - ENA info has been updated.'
        message = (
            "Project information from ENA has been updated.\n\n"
            "New ENA Additions (total in parentheses)\n"
            "Studies: {0} ({1})\n"
            "Experiments: {2} ({3})\n"
            "Runs: {4} ({5})\n\n"
        ).format(
            self.studies_created,
            len(self.ena_studies),
            self.exps_created,
            len(self.ena_exps),
            self.runs_created,
            len(self.ena_runs)
        )
        recipients = ['admin@staphopia.com', 'robert.petit@emory.edu']
        email = EmailMessage(subject, message, labrat, recipients)
        email.send(fail_silently=False)
