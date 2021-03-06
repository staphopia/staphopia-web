"""Pull a list of gene sequences for each published sample."""
from django.db import transaction
from django.core.management.base import BaseCommand

from ena.models import ToPublication
from gene.models import Clusters, Features
from mlst.models import Srst2
from sample.models import Sample, Publication
from sequence.models import Stat


class Command(BaseCommand):
    """Pull a list of gene sequences for each published sample."""

    help = 'Pull a list of gene sequences for each published sample.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('gene_list', metavar='GENE_LIST',
                            help=('A list of UniRef90 genes to pull sequences '
                                  'for. Genes should be in the format of an '
                                  'exported tab list from UniRef90.'))
        parser.add_argument('prefix', metavar='PREFIX',
                            help=('A prefix to add to the output of the FASTA '
                                  'sequences.'))
        parser.add_argument('--all_ranks', action='store_true',
                            help='Include all ranks, not just gold.')
        parser.add_argument('--unpublished', action='store_true',
                            help='Include unpublished samples as well.')
        parser.add_argument('--limit', dest='limit', type=int,
                            help='Limit the number of experiments to output.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Pull a list of gene sequences for each published sample."""
        min_rank = 0 if opts['all_ranks'] else 3
        samples = self.get_samples(not opts['unpublished'],
                                   limit=opts['limit'])
        accessions = {}
        with open(opts['gene_list'], 'r') as fh:
            """
            UniRef90 Tab Columns
            0:Cluster ID      3:Size               6:Length
            1:Status          4:Cluster Members    7:Identity
            2:Cluster name    5:Organisms
            """
            for line in fh:
                if line.startswith("Cluster ID"):
                    continue
                cols = line.rstrip().split('\t')
                accessions[cols[0]] = {
                    'name': cols[2],
                    'status': cols[1],
                    'cluster_size': cols[3],
                    'length': cols[6]
                }

        uniref90_faa = open('{0}-uniref90.faa'.format(opts['prefix']), 'w')
        hits_fna = open('{0}.fna'.format(opts['prefix']), 'w')
        hits_faa = open('{0}.faa'.format(opts['prefix']), 'w')
        hits_txt = open('{0}-uniref-to-ncbi.txt'.format(opts['prefix']), 'w')
        hits_txt.write(('uniref90_id\tsra_experiment\tpmid\trank\tmlst\t'
                        'is_exact\n'))

        for accession, val in accessions.items():
            # Get cluster ids
            try:
                c = Clusters.objects.get(name=accession)
                uniref_header = '{0};{1};{2}'.format(
                    c.name, val['name'], val['status'],
                )
                self.write_fasta(uniref90_faa, uniref_header, c.aa)
                print("{0} processing".format(accession))
                for f in self.get_features(c, not opts['unpublished']):
                    print("\t{0} hit, writing to fasta".format(f.sample.sample_tag))
                    sample = samples[f.sample_id]
                    if (self.test_rank(sample['rank'], min_rank)):
                        hits_txt.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(
                            c.name,
                            sample['tag'],
                            ','.join(self.get_pmids(sample['tag'])),
                            sample['rank'],
                            sample['mlst'],
                            sample['is_exact']
                        ))

                        seq_header = '{0};{1};{2}'.format(
                            sample['tag'], c.name, val['name']
                        )

                        self.write_fasta(hits_fna, seq_header, f.dna)
                        self.write_fasta(hits_faa, seq_header, f.aa)
            except Clusters.DoesNotExist:
                print('{0} does not exist in the database, skipping...'.format(
                    accession
                ))

        uniref90_faa.close()
        hits_fna.close()
        hits_faa.close()
        hits_txt.close()

    def get_features(self, cluster, is_published):
        """Return a Feature table query set."""
        if is_published:
            return Features.objects.filter(cluster=cluster,
                                           sample__is_published=True)
        else:
            return Features.objects.filter(cluster=cluster)

    def test_rank(self, rank, min_rank):
        """Test if given rank is above the minimum rank to print."""
        return rank >= min_rank

    def get_samples(self, is_published, limit=None):
        """Get a list of sample ids that have been published."""
        samples = {}
        if is_published:
            query_set = Sample.objects.filter(
                is_published=is_published
            )
        else:
            query_set = SampleSummary.objects.filter()

        if limit:
            query_set = query_set[:limit]

        for sample in query_set:
            mlst = Srst2.objects.get(sample=sample)
            stat = Stat.objects.get(sample=sample, is_original=False)
            samples[sample.id] = {
                'tag': sample.sample_tag,
                'rank': stat.rank,
                'mlst': mlst.st_stripped,
                'is_exact': mlst.is_exact
            }
        print(len(samples))
        return samples

    def get_rank(self, sample):
        return Stat.objects.filter(sample=sample, is_original=False)

    def get_pmids(self, tag):
        """Get associated PubMed IDs."""
        pmids = []
        for pubmed in ToPublication.objects.filter(experiment_accession=tag):
            pub = Publication.objects.get(id=pubmed.publication_id)
            pmids.append(pub.pmid)
        return pmids

    def write_fasta(self, file_handle, header, seq):
        """Write the FASTA entry."""
        n = 80
        split_seq = [seq[i:i+n] for i in range(0, len(seq), n)]
        file_handle.write('>{0}\n{1}\n'.format(header, '\n'.join(split_seq)))
