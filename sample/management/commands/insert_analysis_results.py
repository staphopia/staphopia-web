"""Insert the results of sample analysis into the database."""

import json

from django.db import transaction
from django.core.management.base import BaseCommand

from sample.tools import prep_insert
from assembly.tools import insert_assembly_stats, insert_assembly_contigs
from mlst.tools import insert_mlst_results
from plasmid.tools import insert_plasmid_stats, insert_plasmid_contigs
from sccmec.tools import insert_sccmec_coverage, insert_sccmec_blast
from sequence.tools import insert_sequence_stats
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
        parser.add_argument('name', metavar='SAMPLE_NAME',
                            help=('Sample tag associated with sample.'))
        parser.add_argument('--force', action='store_true',
                            help='Force updates for existing entries.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""
        # Validate all files are present, will cause error if files are missing
        sample, version, files = prep_insert(
            opts['user'], opts['name'], opts['sample_dir']
        )

        # Insert analysis results
        print(f'{sample.name}: Inserting Sequence Stats...')
        insert_sequence_stats(sample, version, files, force=opts['force'])

        print(f'{sample.name}: Inserting Assembly Stats...')
        insert_assembly_stats(sample, version, files, force=opts['force'])
        insert_assembly_contigs(sample, version, files, force=opts['force'])

        if files['plasmid']:
            print(f'{sample.name}: Inserting Plasmid Assembly Stats...')
            insert_plasmid_stats(sample, version, files, force=opts['force'])
            insert_plasmid_contigs(sample, version, files, force=opts['force'])

        print(f'{sample.name}: Inserting MLST Results...')
        insert_mlst_results(sample, version, files, force=opts['force'])

        '''
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
        '''
