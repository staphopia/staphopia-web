"""Insert the results of sample analysis into the database."""

import json

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from staphopia.utils import md5sum
from sample.models import Sample, ToTag

from sample.tools import (
    create_db_tag, create_tag, validate_analysis, validate_time
)
from assembly.tools import insert_assembly_stats, insert_assembly
from gene.tools import insert_gene_annotations, insert_blast_results
from kmer.tools import insert_kmer_counts
from mlst.tools import insert_mlst_blast, insert_mlst_srst2
from sccmec.tools import insert_sccmec_coverage, insert_sccmec_blast
from sequence.tools import insert_fastq_stats
from variant.tools import insert_variant_results


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
        parser.add_argument('--comment', type=str, default="",
                            help=('Any comments about the project.'))
        parser.add_argument('--db_tag', type=str, default="",
                            help=('Sample tag associated with sample.'))
        parser.add_argument('--strain', type=str, default="",
                            help=('Strain name of the input sample.'))
        parser.add_argument('--is_paired', action='store_true',
                            help='Sample contains paired reads.')
        parser.add_argument('--is_public', action='store_true',
                            help='Sample should be made public.')
        parser.add_argument('--runtime', action='store_true',
                            help='Insert runtimes as well.')
        parser.add_argument('--force', action='store_true',
                            help='Force updates for existing entries.')
        parser.add_argument('--preload', action='store_true',
                            help='Preload UniRef50 clusters into memory.')
        parser.add_argument('--skip_kmers', action='store_true',
                            help="Don't insert kmers stats.")

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
            sample = Sample.objects.get(md5sum=fq_md5sum)
            print("Found existing sample: {0} ({1})".format(
                sample.db_tag, sample.md5sum
            ))
            if not opts['force']:
                raise CommandError(
                    'Sample exists, please use --force to use it.'
                )
            else:
                Sample.objects.filter(md5sum=fq_md5sum).update(
                    sample_tag=opts['sample_tag'],
                    is_paired=opts['is_paired'],
                    is_public=opts['is_public']
                )
        except Sample.DoesNotExist:
            # Create new sample
            try:
                db_tag = create_db_tag(user, db_tag=opts['db_tag'])
                sample = Sample.objects.create(
                    user=user,
                    db_tag=db_tag,
                    sample_tag=opts['sample_tag'],
                    md5sum=fq_md5sum,
                    is_paired=opts['is_paired'],
                    is_public=opts['is_public']
                )
                print("Created new sample: {0}".format(db_tag))
            except IntegrityError as e:
                raise CommandError(
                    'Error, unable to create Sample object. {0}'.format(e)
                )

        if opts['project_tag']:
            tag = create_tag(user, opts['project_tag'], opts['comment'])
            try:
                ToTag.objects.get_or_create(sample=sample, tag=tag)
                print("Project tag '{0}' saved".format(opts['project_tag']))
            except IntegrityError as e:
                raise CommandError(
                    'Error, unable to link Sample to Tag. {0}'.format(e)
                )

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

        print("Inserting Variants...")
        insert_variant_results(files['variants'], sample, force=opts['force'])

        print("Inserting Gene Annotations...")
        insert_gene_annotations(
            files['annotation_genes'], files['annotation_proteins'],
            files['annotation_contigs'], files['annotation_gff'],
            sample, compressed=True, force=opts['force'],
            preload=opts['preload']
        )

        blastp = [
            files['annotation_blastp_proteins'],
            files['annotation_blastp_staph'],
            files['annotation_blastp_sprot']
        ]
        insert_blast_results(
            blastp, files['annotation_gff'], sample, compressed=True,
            force=opts['force']
        )

        if not opts['skip_kmers']:
            print("Inserting k-mer counts...")
            insert_kmer_counts(files['kmers'], sample, force=opts['force'])
        else:
            print("Skipping k-mer counts...")

        print(json.dumps({
            'sample_id': sample.pk,
            'db_tag':sample.db_tag,
            'sample_tag': sample.sample_tag,
            'project_tag': sample.project_tag,
            'strain': sample.strain,
            'is_paired': sample.is_paired,
            'comment': sample.comments
        }))

        # if opts['runtime']:
        #    runtimes = validate_time(opts['sample_dir'])
