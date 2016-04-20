"""Insert the results of sample analysis into the database."""

import json

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from staphopia.utils import md5sum
from sample.models import MetaData

from sample.tools import create_db_tag, validate_analysis, validate_time
from assembly.tools import insert_assembly_stats, insert_assembly
from gene.tools import insert_gene_annotations
from mlst.tools import insert_mlst_blast, insert_mlst_srst2
from sccmec.tools import insert_sccmec_coverage, insert_sccmec_blast
from sequence.tools import insert_fastq_stats
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
        parser.add_argument('--db_tag', type=str, default="",
                            help=('Sample tag associated with sample.'))
        parser.add_argument('--strain', type=str, default="",
                            help=('Strain name of the input sample.'))
        parser.add_argument('--comment', type=str, default="",
                            help=('Any comments about the sample.'))
        parser.add_argument('--is_paired', action='store_true',
                            help='Sample contains paired reads.')
        parser.add_argument('--runtime', action='store_true',
                            help='Insert runtimes as well.')
        parser.add_argument('--force', action='store_true',
                            help='Force updates for existing entries.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""
        # Validate all files are present
        print("Validating required files are present...")
        files = validate_analysis(opts['sample_dir'], opts['sample_tag'])
        fq_md5sum = md5sum('{0}/{1}.cleanup.fastq.gz'.format(
            opts['sample_dir'], opts['sample_tag']
        ))

        # Get User
        try:
            user = User.objects.get(username=opts['user'])
        except User.DoesNotExist:
            raise CommandError('user: {0} does not exist'.format(
                opts['user']
            ))

        # Test if results already inserted
        sample = None
        try:
            sample = MetaData.objects.get(md5sum=fq_md5sum)
            print("Found existing sample: {0} ({1})".format(
                sample.db_tag, sample.md5sum
            ))
            if not opts['force']:
                raise CommandError(
                    'Sample exists, please use --force to use it.'
                )
            else:
                sample.sample_tag = opts['sample_tag']
                sample.project_tag = opts['project_tag'],
                sample.strain = opts['strain'],
                sample.is_paired = opts['is_paired'],
                sample.comments = opts['comment']
                sample.save()
        except MetaData.DoesNotExist:
            # Create new sample
            try:
                db_tag = create_db_tag(user, db_tag=opts['db_tag'])
                sample = MetaData.objects.create(
                    user=user,
                    db_tag=db_tag,
                    sample_tag=opts['sample_tag'],
                    project_tag=opts['project_tag'],
                    md5sum=fq_md5sum,
                    strain=opts['strain'],
                    is_paired=opts['is_paired'],
                    comments=opts['comment']
                )
                print("Created new sample: {0}".format(db_tag))
            except IntegrityError as e:
                raise CommandError(
                    'Error, unable to create Sample object. {0}'.format(e)
                )

        # Verify
        """
        print(json.dumps({
            'sample_id': sample.pk,
            'sample_tag': sample.sample_tag,
            'project_tag': sample.project_tag,
            'strain': sample.strain,
            'is_paired': sample.is_paired,
            'comment': sample.comments
        }))
        """

        # Insert analysis results
        print("Inserting Sequence Stats...")
        insert_fastq_stats(files['stats_filter'], sample, is_original=False,
                           force=opts['force'])
        insert_fastq_stats(files['stats_original'], sample, is_original=True,
                           force=opts['force'])

        print("Inserting Assembly Stats...")
        insert_assembly_stats(files['contigs'], sample, is_scaffolds=False,
                              force=opts['force'])
        insert_assembly_stats(files['scaffolds'], sample, is_scaffolds=True,
                              force=opts['force'])
        insert_assembly(files['assembly'], sample, force=opts['force'])

        print("Inserting MLST Results...")
        insert_mlst_blast(files['mlst_blast'], sample, force=opts['force'])
        insert_mlst_srst2(files['mlst_srst2'], sample, force=opts['force'])

        print("Inserting SCCmec Coverage Stats...")
        insert_sccmec_coverage(files['sccmec_coverage'], sample,
                               force=opts['force'])
        insert_sccmec_blast(files['sccmec_primers'], sample, is_primers=True,
                            force=opts['force'])
        insert_sccmec_blast(files['sccmec_proteins'], sample, is_primers=False,
                            force=opts['force'])


        # if opts['runtime']:
        #    runtimes = validate_time(opts['sample_dir'])
        """




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
