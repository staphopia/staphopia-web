"""
For all samples, create a a fasta representation of the assembly and genes.
"""
import os

from django.core.management.base import BaseCommand, CommandError

from api.queries.assemblies import get_assembly_contigs
from api.queries.genes import get_genes_by_sample
from api.utils import query_database

from staphopia.utils import gzip_file


class Command(BaseCommand):
    """For all samples, create a document for full text searches."""

    help = 'For all samples, create a document for full text searches.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('output', metavar='OUTPUT_DIRECTORY',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('--debug', action='store_true',
                            help=('Create fasta for a single sample.'))
        parser.add_argument('--ena', action='store_true',
                            help=('Create fasta for ena samples only.'))

    def handle(self, *args, **opts):
        """For all samples, create a document for full text searches."""
        sql = """SELECT sample_id, name
                 FROM sample_basic
                 {0}
                 ORDER BY sample_id;""".format(
            'WHERE user_id=1' if opts['ena'] else ''
        )

        if os.path.exists(opts['output']):
            print(f'{opts["output"]} exists already, will skip existing files')
        else:
            os.mkdir(f'{opts["output"]}')
            os.mkdir(f'{opts["output"]}/genes')
            os.mkdir(f'{opts["output"]}/proteins')
            os.mkdir(f'{opts["output"]}/contigs')

        for sample in query_database(sql):
            print(f"Working on {sample['name']} ({sample['sample_id']})")
            # .ffn - gene sequences
            # .faa - protein sequences
            genes = f'{opts["output"]}/genes/{sample["name"]}.ffn'
            proteins = f'{opts["output"]}/proteins/{sample["name"]}.faa'

            if not os.path.exists(f'{genes}.gz'):
                with open(genes, 'w') as gene_out, open(proteins, 'w') as prot_out:
                    for gene in get_genes_by_sample([sample['sample_id']], 1):
                        if gene['aa']:
                            prot_out.write(f'>{gene["header"]}\n')
                            prot_out.write(f'{gene["aa"]}\n')
                            gene_out.write(f'>{gene["header"]}\n')
                            gene_out.write(f'{gene["dna"]}\n')
                        else:
                            gene_out.write(f'>{gene["header"]}\n')
                            gene_out.write(f'{gene["dna"]}\n')

                # .fna - contig sequences
                contigs = f'{opts["output"]}/contigs/{sample["name"]}.fna'
                with open(contigs, 'w') as contig_out:
                    for contig in get_assembly_contigs([sample['sample_id']], 1):
                        contig_out.write(f'>{contig["header"]}\n')
                        contig_out.write(f'{contig["sequence"]}\n')

                gzip_file(genes)
                gzip_file(proteins)
                gzip_file(contigs)
            else:
                print(f'Found {genes}.gz, skipping')
            if opts['debug']:
                break
