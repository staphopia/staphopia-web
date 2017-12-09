"""Insert the results of sample analysis into the database."""

import json

from django.db import transaction
from django.core.management.base import BaseCommand

from sample.tools import (
    get_analysis_status, handle_new_sample, update_ena_md5sum
)
from assembly.tools import insert_assembly_stats, insert_assembly
from gene.tools import insert_gene_annotations, insert_blast_results
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
        parser.add_argument('--is_paired', action='store_true',
                            help='Sample contains paired reads.')
        parser.add_argument('--is_public', action='store_true',
                            help='Sample should be made public.')
        parser.add_argument('--is_published', action='store_true',
                            help='Sample is published.')
        parser.add_argument('--skip_existing', action='store_true',
                            help='Skip module if its already in the database.')
        parser.add_argument('--force', action='store_true',
                            help='Force updates for existing entries.')


    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""

        # Validate all files are present, will cause error if files are missing
        print("Validating required files are present...")
        files = get_analysis_status(opts['sample_tag'], opts['sample_dir'])

        # Get FASTQ MD5
        md5sum = None
        with open(files['fastq_md5'], 'r') as fh:
            for line in fh:
                md5sum = line.rstrip()

        # Get or create a new Sample
        if opts['update_ena_md5sum']:
            update_ena_md5sum(opts['user'], opts['sample_tag'], md5sum)

        sample_info = {
            'sample_tag': opts['smaple_tag'],
            'is_paired': True if 'fastq_r2' in files else False,
            'is_public': opts['is_public'],
            'is_published': opts['is_published']
        }

        project_info = None
        if opts['project_tag']:
            project_info = {
                'tag': opts['project_tag'],
                'comment': opts['comment']
            }

        sample = handle_new_sample(
            sample_info, opts['user'], md5sum, force=opts['force'],
            skip_existing=opts['skip_existing'], project_info=project_info
        )

        # Insert analysis results
        print("Inserting Sequence Stats...")
        insert_fastq_stats(files['stats_filter'], sample, is_original=False,
                           force=opts['force'], skip=opts['skip_existing'])
        insert_fastq_stats(files['stats_original'], sample, is_original=True,
                           force=opts['force'], skip=opts['skip_existing'])

        print("Inserting Assembly Stats...")
        insert_assembly_stats(files['contigs'], sample, is_scaffolds=False,
                              force=opts['force'], skip=opts['skip_existing'])
        insert_assembly_stats(files['scaffolds'], sample, is_scaffolds=True,
                              force=opts['force'], skip=opts['skip_existing'])
        insert_assembly(files['assembly'], sample, force=opts['force'],
                        skip=opts['skip_existing'])

        if files['plasmid']:
            print("Inserting Plasmid Assembly Stats...")
            insert_assembly_stats(files['plasmid-contigs'], sample,
                                  is_scaffolds=False, force=opts['force'],
                                  is_plasmids=True, skip=opts['skip_existing'])
            insert_assembly_stats(files['plasmid-scaffolds'], sample,
                                  is_scaffolds=True, force=opts['force'],
                                  is_plasmids=True, skip=opts['skip_existing'])
            insert_assembly(files['plasmid-assembly'], sample,
                            is_plasmids=True, force=opts['force'],
                            skip=opts['skip_existing'])
        else:
            print("No Plasmid Assembly Stats To Insert...")

        print("Inserting MLST Results...")
        insert_mlst_blast(files['mlst_blast'], sample, force=opts['force'],
                          skip=opts['skip_existing'])
        insert_mlst_srst2(files['mlst_srst2'], sample, force=opts['force'],
                          skip=opts['skip_existing'])

        print("Inserting SCCmec Coverage Stats...")
        insert_sccmec_coverage(files['sccmec_coverage'], sample,
                               force=opts['force'], skip=opts['skip_existing'])
        insert_sccmec_blast(files['sccmec_primers'], sample, is_primers=True,
                            force=opts['force'], skip=opts['skip_existing'])
        insert_sccmec_blast(files['sccmec_proteins'], sample, is_primers=False,
                            force=opts['force'], skip=opts['skip_existing'])
        insert_sccmec_blast(files['sccmec_subtypes'], sample, is_primers=False,
                            is_subtype=True, force=opts['force'],
                            skip=opts['skip_existing'])

        print("Inserting Variants...")
        insert_variant_results(files['variants'], sample, force=opts['force'],
                               skip=opts['skip_existing'])

        print("Inserting Gene Annotations...")
        insert_gene_annotations(
            files['annotation_genes'], files['annotation_proteins'],
            files['annotation_contigs'], files['annotation_gff'],
            sample, compressed=True, force=opts['force'],
            skip=opts['skip_existing']
        )

        blastp = [
            files['annotation_blastp_proteins'],
            files['annotation_blastp_staph'],
            files['annotation_blastp_sprot']
        ]
        insert_blast_results(
            blastp, files['annotation_gff'], sample, compressed=True,
            force=opts['force'], skip=opts['skip_existing']
        )

        print(json.dumps({
            'sample_id': sample.pk,
            'sample_tag': sample.sample_tag,
            'project_tag': opts['project_tag'],
            'is_paired': sample.is_paired,
            'comment': opts['comment']
        }))
