"""Insert the results of sample analysis into the database."""

import json

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from sample.tools import prep_insert
from annotation.tools import insert_annotation
from assembly.tools import insert_assembly
from cgmlst.tools import insert_cgmlst
from mlst.tools import insert_mlst
from plasmid.tools import insert_plasmid
from resistance.tools import insert_resistance
from sccmec.tools import insert_sccmec
from sequence.tools import insert_sequence_stats
from variant.tools import insert_variants
from virulence.tools import insert_virulence


class Command(BaseCommand):
    """Insert the results of sample analysis into the database."""

    help = 'Insert the results of sample analysis into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('user', metavar='USERNAME',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('sample_dir', metavar='SAMPLE_DIRECTORY',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('name', metavar='SAMPLE_NAME',
                            help=('Sample tag associated with sample.'))
        parser.add_argument('--force', action='store_true',
                            help='Force updates for existing entries.')
        parser.add_argument('--is_public', action='store_true',
                            help='Sample should be made public.')
        parser.add_argument('--is_published', action='store_true',
                            help='Sample is published.')
        parser.add_argument('--tag', type=str,
                            help='A tag to associate the sampel with.')
        parser.add_argument('--comment', type=str,
                            help='Any comments about the sample.')

    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""
        # Validate all files are present, will cause error if files are missing
        sample_info = {
            'name': opts['name'],
            'is_public': opts['is_public'],
            'is_published': opts['is_published']
        }

        project_info = None
        if opts['tag'] and opts['comment']:
            project_info = {
                'tag': opts['tag'],
                'comment': opts['comment']
            }
        elif opts['tag'] or opts['comment']:
            raise CommandError('--tag and --comment must be used together')

        sample, version, files = prep_insert(
            opts['user'], opts['name'], opts['sample_dir'],
            sample_info=sample_info, project_info=project_info
        )

        # Insert analysis results
        print(f'{sample.name}: Inserting Variant Results...')
        insert_variants(sample, version, files, force=opts['force'])

        print(f'{sample.name}: Inserting Sequence Stats...')
        insert_sequence_stats(sample, version, files, force=opts['force'])

        if files['plasmid']:
            print(f'{sample.name}: Inserting Plasmid Assembly Stats...')
            insert_plasmid(sample, version, files, force=opts['force'])

        print(f'{sample.name}: Inserting Annotation Results...')
        insert_annotation(sample, version, files, force=opts['force'])

        print(f'{sample.name}: Inserting MLST/cgMLST Results...')
        insert_mlst(sample, version, files, force=opts['force'])
        #insert_cgmlst(sample, version, files, force=opts['force'])

        print(f'{sample.name}: Inserting Resistance/Virulence Results...')
        if 'resistance_report' in files:
            insert_resistance(sample, version, files, force=opts['force'])
        else:
            print(f'{sample.name}: No Ariba resitance results to report.')

        if 'virulence_report' in files:
            insert_virulence(sample, version, files, force=opts['force'])
        else:
            print(f'{sample.name}: No Ariba virulence results to report.')

        self.insert_dependents(sample, version, files, force=opts['force'])

        print(f'{sample.name}: Done')

    @transaction.atomic
    def insert_dependents(self, sample, version, files, force=False):
        """These tables are linked together, so update/insert together."""
        print(f'{sample.name}: Inserting Assembly Stats...')
        insert_assembly(sample, version, files, force=force)

        print(f'{sample.name}: Inserting SCCmec Results...')
        insert_sccmec(sample, version, files, force=force)
