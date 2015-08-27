""" Insert PROKKA output into the database. """
# from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from staphopia.utils import timeit, gziplines
from samples.models import Sample
from analysis.models import PipelineVersion
from gene.models import Clusters, Contigs, Features


class Command(BaseCommand):
    help = 'Insert annotated gene info generated by PROKKA into the database.'

    def add_arguments(self, parser):
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag of the data.')
        parser.add_argument('gff', metavar='GFF3_GZIP',
                            help=('PROKKA annotations in GFF3 format (output '
                                  'with .gff.gz extension)'))
        parser.add_argument('contigs', metavar='FNA_GZIP',
                            help=('Assembled contigs renamed by PROKKA (output'
                                  ' with .fna.gz extension)'))
        parser.add_argument('genes', metavar='FFN_GZIP',
                            help=('Predicted gene sequences from PROKKA ('
                                  'output with .ffn.gz extension)'))
        parser.add_argument('proteins', metavar='FAA_GZIP',
                            help=('Predicted protein sequences from PROKKA ('
                                  'output with .faa.gz extension)'))
        parser.add_argument('--pipeline_version', type=str, default="0.1",
                            help=('Version of the pipeline used in this '
                                  'analysis. (Default: 0.1)'))

    def handle(self, *args, **opts):
        # Get Sample instance
        try:
            self.sample = Sample.objects.get(sample_tag=opts['sample_tag'])
        except Sample.DoesNotExist:
            raise CommandError('sample_tag {0} does not exist'.format(
                opts['sample_tag']
            ))

        # Get PipelineVersion instance
        try:
            self.pipeline_version = PipelineVersion.objects.get_or_create(
                module='gene',
                version=opts['pipeline_version']
            )[0]
        except PipelineVersion.DoesNotExist:
            raise CommandError('Error saving pipeline information')

        # Read Fasta files
        self.contigs = self.read_fasta(opts['contigs'])
        self.genes = self.read_fasta(opts['genes'])
        self.proteins = self.read_fasta(opts['proteins'])

        # Insert contigs to database
        self.contig_pks = self.insert_contigs()

        # Read GFF3 File
        self.read_gff(opts['gff'])

    @timeit
    def read_fasta(self, fasta):
        id = None
        seq = []
        records = {}
        for line in gziplines(fasta):
            line = line.rstrip()
            if line.startswith('>'):
                if len(seq):
                    records[id] = ''.join(seq)
                    seq = []
                id = line[1:].split(' ')[0]
            else:
                seq.append(line)

        records[id] = ''.join(seq)

        return records

    @timeit
    def insert_contigs(self):
        pks = {}
        for name, sequence in self.contigs.items():
            try:
                contig, created = Contigs.objects.get_or_create(
                    sample=self.sample,
                    name=name,
                    sequence=sequence
                )
                pks[name] = contig.pk
            except IntegrityError as e:
                raise CommandError('Error inserting contigs: {1}'.format(e))

        return pks

    def get_cluster_pk(self, cluster):
        return Clusters.objects.get(name=cluster).values('id')

    @timeit
    def read_gff(self, gff_file):
        records = []
        types = ['CDS', 'tRNA']

        for line in gziplines(gff_file):
            if line.startswith('##'):
                # Don't need these lines
                if line.startswith('##FASTA'):
                    # Don't read the sequence
                    break
                continue
            else:
                '''
                Parse the feature
                Columns: 0:contig       3:start       6:strand
                         1:source       4:end         7:phase
                         2:type         5:score       8:attributes

                Example: Attribute
                ID=PROKKA_00001;
                Parent=PROKKA_00001_gene;
                inference=ab initio prediction:Prodigal:2.6,similar to AA
                          sequence:RefSeq:UniRef90_A0A0D1GFR5;
                locus_tag=PROKKA_00001;
                product=Strain SA-120 Contig630%2C whole genome shotgun
                        sequence;
                protein_id=gnl|PROKKA|PROKKA_00001
                '''
                # Only parse those features of type in types
                cols = line.split('\t')
                if cols[2] in types:
                    # Parse attributes
                    cluster = 'NO_MATCHING_CLUSTER'
                    id = None
                    for attribute in cols[8].split(';'):
                        if attribute.startswith('ID'):
                            id = attribute.split('=')[1]
                        elif attribute.startswith('inference'):
                            cluster = 'UniRef90_{0}'.format(
                                attribute.split('UniRef90_')[1]
                            )

                    records.append(
                        Features(
                            sample=self.sample,
                            version=self.pipeline_version,
                            contig_id=self.contig_pks[cols[0]],
                            cluster_id=self.get_cluster_pk(cluster),

                            start=int(cols[3]),
                            end=int(cols[4]),
                            is_positive=True if cols[6] == '+' else False,
                            is_tRNA=True if cols[2] == 'tRNA' else False,
                            phase=int(cols[7]),

                            dna=self.genes[id],
                            aa=self.proteins[id],
                        )
                    )