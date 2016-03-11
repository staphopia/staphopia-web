"""
Useful functions associated with gene.

To use:
from gene.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.constants import UNIREF90
from staphopia.utils import timeit, gziplines, read_fasta
from gene.models import Clusters, Contigs, Features


@transaction.atomic
def insert_gene_annotations(files, sample, compressed=True):
    """Insert gene annotations into the database."""
    genes = read_fasta(files['genes'], compressed=True)
    proteins = read_fasta(files['proteins'], compressed=True)
    contig_pks = __insert_contigs(files['contigs'], sample, compressed)
    features = __read_gff(files['gff'], sample, contig_pks, genes, proteins)
    Features.objects.bulk_create(features, batch_size=500)


@transaction.atomic
def __insert_contigs(contigs, sample, compressed):
    """Insert contigs into the database."""
    pks = {}
    contigs = read_fasta(contigs, compressed)
    for name, sequence in contigs.items():
        try:
            contig, created = Contigs.objects.get_or_create(
                sample=sample,
                name=name,
                sequence=sequence
            )
            pks[name] = contig.pk
        except IntegrityError as e:
            raise CommandError('Error inserting contigs: {0}'.format(e))

    return pks


def __get_cluster_pk(cluster):
    try:
        cluster = Clusters.objects.get(name=cluster)
    except Clusters.DoesNotExist:
        from subprocess import Popen, PIPE
        print(cluster)
        f = Popen(['grep', cluster, UNIREF90], stdout=PIPE)
        stdout, stderr = f.communicate()
        name, seq = stdout.rstrip().split('\t')
        cluster = Clusters.objects.create(name=name, aa=seq)
    return cluster.pk


@timeit
def __read_gff(gff_file, sample, contig_pks, genes, proteins):
    features = []
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
                        if 'UniRef90_' in attribute:
                            cluster = 'UniRef90_{0}'.format(
                                attribute.split('UniRef90_')[1]
                            )

                if cols[7] == '.':
                    # tRNA gives '.' for phase,lets make it 9
                    cols[7] = 9

                features.append(
                    Features(
                        sample=sample,
                        contig_id=contig_pks[cols[0]],
                        cluster_id=__get_cluster_pk(cluster),

                        start=int(cols[3]),
                        end=int(cols[4]),
                        is_positive=True if cols[6] == '+' else False,
                        is_tRNA=True if cols[2] == 'tRNA' else False,
                        phase=int(cols[7]),

                        dna=genes[id] if id in genes else '',
                        aa=proteins[id] if id in proteins else '',
                    )
                )

    return features
