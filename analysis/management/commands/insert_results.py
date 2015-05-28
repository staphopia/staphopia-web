""" Insert JSON formatted analysis results into database. """
import json
import os.path
from optparse import make_option

from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from samples.models import Sample
from analysis.models import FastqStat, AssemblyStat, PipelineVersion


class Command(BaseCommand):

    """ Insert results into database. """

    help = 'Insert the analysis results into the database.'

    option_list = BaseCommand.option_list + (
        make_option('--sample_tag', dest='sample_tag',
                    help='Sample tag for which the data is for'),
        make_option('--table', dest='table',
                    help=('Table (fastq_original, fastq_clean, '
                          'assembly_contigs, assembly_scaffolds) to '
                          'insert data into.')),
        make_option('--input', dest='input',
                    help='JSON formated file containing data to be inserted'),
        make_option('--pipeline_version', dest='pipeline_version',
                    help=('Version of the pipeline used in this analysis. '
                          '(Default: 0.1)')),
        make_option('--debug', action='store_true', dest='debug',
                    default=False, help='Will not write to the database'),
    )

    def handle(self, *args, **opts):
        """ Insert results to database. """
        # Required Parameters
        if not opts['sample_tag']:
            raise CommandError('--sample_tag is requried')
        elif not opts['table']:
            raise CommandError('--table is requried')
        elif not opts['input']:
            raise CommandError('--input is requried')
        elif not opts['pipeline_version']:
            opts['pipeline_version'] = "0.1"

        # Sample
        try:
            sample = Sample.objects.get(sample_tag=opts['sample_tag'])
        except Sample.DoesNotExist:
            raise CommandError('sample_tag: {0} does not exist'.format(
                opts['sample_tag']
            ))

        # Database Table
        accepted_tables = ['fastq_original', 'fastq_clean', 'assembly_contigs',
                           'assembly_scaffolds']
        if opts['table'] not in accepted_tables:
            raise CommandError(
                'Unknown table: {0}. Use one of the following: {1}'.format(
                    opts['table'],
                    ', '.join(accepted_tables)
                )
            )

        # Input File
        if not os.path.exists(opts['input']):
            raise CommandError('{0} does not exist'.format(opts['input']))

        # Pipeline Version
        try:
            module = opts['table'].split('_')[0]
            pipeline_version = PipelineVersion.objects.get_or_create(
                module=module,
                version=opts['pipeline_version']
            )[0]
        except PipelineVersion.DoesNotExist:
            raise CommandError('Error saving pipeline information')

        # JSON input
        try:
            with open(opts['input'], 'r') as f:
                json_data = json.loads(f.readline().rstrip())
        except ValueError as e:
            raise CommandError('{0}: invalid JSON'.format(opts['input']))

        # Everything checks out, load it up
        table_object = None
        if opts['table'].startswith('fastq'):
            is_original = False if opts['table'] == 'fastq_clean' else True
            table_object = FastqStat(
                sample=sample,
                is_original=is_original,
                rank=self.get_rank(json_data),
                version_id=pipeline_version.pk,
                **json_data
            )
        elif opts['table'].startswith('assembly'):
            is_scaffolds = False if opts['table'].endswith('contigs') else True
            table_object = AssemblyStat(
                sample=sample,
                is_scaffolds=is_scaffolds,
                version_id=pipeline_version.pk,
                **json_data
            )

        if not opts['debug']:
            try:
                table_object.save()
                print 'Saved results'
            except IntegrityError as e:
                raise CommandError(('{0}. Either the data is already in '
                                    'there or the pipeline version should '
                                    'be updated.').format(e))
        else:
            print 'Did not save results'

    def get_rank(self, data):
        """
        Determine the rank of the reads.

        3: Gold, 2: Silver, 1: Bronze
        """
        if data['mean_read_length'] >= 95:
            if data['coverage'] >= 45 and data['qual_mean'] >= 30:
                return 3
            elif data['coverage'] >= 20 and data['qual_mean'] >= 20:
                return 2
            else:
                return 1
        else:
            return 1
