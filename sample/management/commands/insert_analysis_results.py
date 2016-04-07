"""Insert the results of sample analysis into the database."""

import json

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from sample.models import MetaData

from sample.tools import create_sample_tag, validate_analysis, validate_time
from assembly.tools import insert_assembly_stats
from gene.tools import insert_gene_annotations
from mlst.tools import insert_mlst_blast, insert_mlst_srst2
from sccmec.tools import insert_sccmec_coverage
from sequence.tools import insert_sequence_stats
from variant.tools import Variants


class Command(BaseCommand):
    """Insert the results of sample analysis into the database."""

    help = 'Insert the results of sample analysis into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('user', metavar='USERNAME',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('sample_dir', metavar='SAMPLE_DIRECTORY',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help=('Sample tag associated with sample.'))
        parser.add_argument('--project_tag', type=str, default="",
                            help='(Associate sample with a given tag. ('
                                 'Example: ga-outbreak, vanA-samples, etc...')
        parser.add_argument('--strain', type=str, default="",
                            help=('Strain name of the input sample.'))
        parser.add_argument('--comment', type=str, default="",
                            help=('Any comments aboutthe sample.'))
        parser.add_argument('--is_paired', action='store_true',
                            help='Sample contains paired reads.')
        parser.add_argument('--runtime', action='store_true',
                            help='Insert runtimes as well.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""
        # Validate all files are present
        print("Validating required files are present...")
        files = validate_analysis(opts['sample_dir'], opts['sample_tag'])

        print(files)

        if opts['runtime']:
            runtimes = validate_time(opts['sample_dir'])
            print(runtimes)
        """
        if not files["missing"]:
            try:
                user = User.objects.get(username=opts['user'])
            except User.DoesNotExist:
                raise CommandError('user: {0} does not exist'.format(
                    opts['user']
                ))

            # Create new sample
            try:
                sample_tag = create_sample_tag(user)
                print("Creating new sample: {0}".format(sample_tag))
                sample = MetaData(
                    user=user,
                    sample_tag=sample_tag,
                    project_tag=opts['project_tag'],
                    strain=opts['strain'],
                    is_paired=opts['is_paired'],
                    comments=opts['comment']
                )
                sample.save()
            except IntegrityError as e:
                raise CommandError(
                    'Error, unable to create Sample object. {0}'.format(e)
                )

            # Verify
            '''
            print(json.dumps({
                'sample_id': sample.pk,
                'sample_tag': sample.sample_tag,
                'project_tag': sample.project_tag,
                'strain': sample.strain,
                'is_paired': sample.is_paired,
                'comment': sample.comments
            }))
            '''

            # Insert analysis results
            print("\tInserting Sequence Stats...")
            insert_sequence_stats(files['stats_filter'], sample,
                                  is_original=False)
            insert_sequence_stats(files['stats_original'], sample,
                                  is_original=True)

            print("\tInserting Assembly Stats...")
            insert_assembly_stats(files['contigs'], sample, is_scaffolds=False)
            insert_assembly_stats(files['scaffolds'], sample,
                                  is_scaffolds=True)

            print("\tInserting MLST Results...")
            insert_mlst_blast(files['mlst_blast'], sample)
            insert_mlst_srst2(files['mlst_srst2'], sample)

            print("\tInserting SCCmec Coverage Stats...")
            insert_sccmec_coverage(files['sccmec_coverage'], sample)

            print("\tInserting Gene Annotations...")
            insert_gene_annotations(files['annotation'], sample,
                                    compressed=True)

            print("\tInserting Variants...")
            variants = Variants(files['variants'], sample)
            variants.insert_variants()
        else:
            raise CommandError(
                ('{0} required files were missing.\n\n'
                 'Missing files:\n{1}').format(
                    len(files['missing']),
                    '\n'.join(files['missing'])
                )
            )
        """
