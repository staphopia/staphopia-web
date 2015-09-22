""" Insert JSON formatted analysis results into database. """
import json
import os.path

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from sample.models import MetaData
from sequence.models import Quality


class Command(BaseCommand):
    """ Insert results into database. """
    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag of the data.')
        parser.add_argument('table', metavar='TABLE',
                            help=('Table (original or cleanup) to '
                                  'insert data into.'))
        parser.add_argument('input', metavar='JSON_INPUT',
                            help='JSON formated file to be inserted')

    @transaction.atomic
    def handle(self, *args, **opts):
        """ Insert results to database. """

        # Sample (sample.MetaData)
        try:
            sample = MetaData.objects.get(sample_tag=opts['sample_tag'])
        except MetaData.DoesNotExist:
            raise CommandError('sample_tag: {0} does not exist'.format(
                opts['sample_tag']
            ))

        # Database Table
        accepted_tables = ['original', 'cleanup']
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

        # JSON input
        try:
            with open(opts['input'], 'r') as f:
                json_data = json.loads(f.readline().rstrip())
        except ValueError as e:
            raise CommandError('{0}: invalid JSON'.format(opts['input']))

        # Everything checks out, load it up

        try:
            is_original = False if opts['table'] == 'cleanup' else True
            table_object = Quality(
                sample=sample,
                is_original=is_original,
                rank=self.get_rank(json_data),
                **json_data
            )
            table_object.save()
            print 'Saved results'
        except IntegrityError as e:
            raise CommandError(
                ('{0}. Either the data is already in there or the pipeline '
                 'version should be updated.').format(e)
            )

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
