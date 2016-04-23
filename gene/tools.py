"""
Useful functions associated with gene.

To use:
from gene.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from assembly.models import Contigs
from gene.models import (
    Clusters, Features, Note, Product, Inference, BlastResults
)

from staphopia.constants import UNIREF50
from staphopia.utils import timeit, gziplines, read_fasta, read_json
from sample.tools import get_program_id


def insert_gene_annotations(genes, proteins, contigs, gff, sample,
                            compressed=True, force=False, preload=False):
    """Insert gene annotations into the database."""
    if force:
        delete_features(sample)

    genes = read_fasta(genes, compressed=True)
    proteins = read_fasta(proteins, compressed=True)
    contigs = get_contigs(contigs, sample)
    features = read_gff(gff, sample, contigs, genes, proteins, preload=preload)
    insert_features(features)


@transaction.atomic
def insert_blast_results(files, gff, sample, compressed=True, force=False):
    """Insert blast results for predicted genes into the database."""
    if force:
        print("\tForce used, emptying Gene blast related results.")
        BlastResults.objects.filter(sample=sample).delete()

    features = get_features(sample)
    id_map = get_id_mappings(gff)
    hits = []
    program = None
    for file in files:
        json_data = read_json(file, compressed=compressed)
        for entry in json_data['BlastOutput2']:
            hit = entry['report']['results']['search']
            if len(hit['hits']):
                if not program:
                    program = get_program_id(
                        entry['report']['program'],
                        entry['report']['version'],
                        'database:{0}'.format(
                            entry['report']['search_target']['db']
                        )
                    )
                prokka_id = id_map[hit['query_title']]
                feature = features[prokka_id]

                # Only storing the top hit
                hsp = hit['hits'][0]['hsps'][0]

                # Includes mismatches and gaps
                mismatch = hsp['align_len'] - hsp['identity']

                # Hamming distance
                hd = mismatch
                if hit['query_len'] > hsp['align_len']:
                    # Include those bases that weren't aligned
                    hd = hit['query_len'] - hsp['align_len'] + mismatch

                hits.append(BlastResults(
                    sample=sample,
                    feature=feature,
                    program=program,

                    bitscore=int(hsp['bit_score']),
                    evalue=hsp['evalue'],
                    identity=hsp['identity'],
                    mismatch=mismatch,
                    gaps=hsp['gaps'],
                    hamming_distance=hd,
                    query_from=hsp['query_from'],
                    query_to=hsp['query_to'],
                    query_len=hit['query_len'],
                    hit_from=hsp['hit_from'],
                    hit_to=hsp['hit_to'],
                    align_len=hsp['align_len'],

                    qseq=hsp['qseq'],
                    hseq=hsp['hseq'],
                    midline=hsp['midline']
                ))

    try:
        BlastResults.objects.bulk_create(hits, batch_size=5000)
        print('\tGene BlastResults saved.')
    except IntegrityError as e:
        raise CommandError('{0} Gene BlastResults Error: {1}'.format(
            sample.sample_tag, e
        ))


"""
    bitscore = models.PositiveSmallIntegerField()
    evalue = models.DecimalField(max_digits=7, decimal_places=2)
    identity = models.PositiveSmallIntegerField()
    mismatch = models.PositiveSmallIntegerField()
    gaps = models.PositiveSmallIntegerField()
    hamming_distance = models.PositiveSmallIntegerField()
    query_from = models.PositiveSmallIntegerField()
    query_to = models.PositiveSmallIntegerField()
    hit_from = models.PositiveIntegerField()
    hit_to = models.PositiveIntegerField()
    align_len = models.PositiveSmallIntegerField()

    qseq = models.TextField()
    hseq = models.TextField()
    midline = models.TextField()"""

def get_features(sample):
    """Return a dict of features indexed by prokka id."""
    rows = {}
    for tag in Features.objects.filter(sample=sample):
        rows[tag.prokka_id] = tag
    return rows


def get_id_mappings(gff):
    """Get prokka CDS id mappings from GFF."""
    types = ['CDS']
    done_reading = False
    query_titles = {}
    for line in gziplines(gff):
        if done_reading:
            continue
        line = line.rstrip()
        if line.startswith('##'):
            # Don't need these lines
            if line.startswith('##FASTA'):
                # Done, process no more
                done_reading = True
            continue
        else:
            # Only parse those features of type in types
            cols = line.split('\t')
            if cols[2] in types:
                attributes = dict( a.split('=') for a in cols[8].split(';'))
                query_titles[attributes['query_title']] = attributes['ID']
    return query_titles


@transaction.atomic
def delete_features(sample):
    """Delete features associated with a sample."""
    print("\tForce used, emptying Annotation related results.")
    Features.objects.filter(sample=sample).delete()

@transaction.atomic
def insert_features(features):
    """Bulk insert a list of features."""
    Features.objects.bulk_create(features, batch_size=500)


@transaction.atomic
def get_contigs(contigs, sample):
    """Insert contigs into the database."""
    pks = {}
    with open(contigs, 'r') as fh:
        for line in fh:
            original, renamed = line.rstrip().split('\t')
            try:
                contig = Contigs.objects.get(
                    sample=sample,
                    name=original
                )
                pks[renamed] = contig
            except IntegrityError as e:
                raise CommandError('Error getting contig: {0}'.format(e))
    return pks


def get_clusters():
    """Get the total list of clusters."""
    rows = {}
    for tag in Clusters.objects.filter():
        rows[tag.name] = tag
    return rows


def get_notes():
    """Get the total list of notes."""
    rows = {}
    for tag in Note.objects.filter():
        rows[tag.note] = tag
    return rows


def get_inferences():
    """Get the total list of inferences."""
    rows = {}
    for tag in Inference.objects.filter():
        rows[tag.inference] = tag
    return rows


def get_products():
    """Get the total list of products."""
    rows = {}
    for tag in Product.objects.filter():
        rows[tag.product] = tag
    return rows


@transaction.atomic
def create_cluster(cluster, preloaded_clusters=None):
    """Get or create a cluster."""
    try:
        name = None
        seq = None
        if preloaded_clusters:
            if cluster in preloaded_clusters:
                name = cluster
                seq = preloaded_clusters[cluster]
            else:
                # no-matching-cluster
                name = cluster
                seq = cluster
        else:
            from subprocess import Popen, PIPE
            f = Popen(['grep', cluster, UNIREF50], stdout=PIPE)
            stdout, stderr = f.communicate()
            if stdout:
                name, seq = stdout.rstrip().split('\t')
            else:
                # no-matching-cluster
                name = cluster
                seq = cluster
            return Clusters.objects.create(name=name, aa=seq)
    except IntegrityError as e:
        raise CommandError('Error getting contig: {0}'.format(e))


def preload_clusters():
    """Preload clusters to prevent, grepping a lot."""
    clusters = {}
    with open(UNIREF50, 'r') as fh:
        for line in fh:
            name, seq = line.rstrip().split('\t')
            clusters[name] = seq
    return clusters


@transaction.atomic
def get_object(key, query, dictionary, model_obj):
    """Get or create a new object instance."""
    if key not in dictionary:
        try:
            obj, c = model_obj.objects.get_or_create(**query)
            dictionary[key] = obj
        except IntegrityError as e:
            raise CommandError('Error saving inference: {0}'.format(e))

    return dictionary


@timeit
def read_gff(gff_file, sample, contigs, genes, proteins, preload=False):
    """Read through the GFF and extract annotations."""
    features = []
    types = ['CDS', 'tRNA', 'rRNA']
    notes = get_notes()
    inferences = get_inferences()
    products = get_products()
    clusters = get_clusters()

    done_reading = False
    preloaded_clusters = preload_clusters() if preload else None
    for line in gziplines(gff_file):
        if done_reading:
            continue
        line = line.rstrip()
        if line.startswith('##'):
            # Don't need these lines
            if line.startswith('##FASTA'):
                # Done, process no more
                done_reading = True
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
                cluster = 'no-matching-cluster'
                product = "none"
                note = "none"

                attributes = dict( a.split('=') for a in cols[8].split(';'))
                prokka_id = attributes['ID']
                if 'inference' in attributes:
                    if 'UniRef50_' in attributes['inference']:
                        cluster = 'UniRef50_{0}'.format(
                            attributes['inference'].split('UniRef50_')[1]
                        )

                if cols[2] in ['tRNA', 'rRNA']:
                    cluster = 'predicted-rna'

                if cluster not in clusters:
                    clusters[cluster] = create_cluster(
                        cluster, preloaded_clusters=preloaded_clusters
                    )

                if 'product' in attributes:
                    product = attributes['product']
                products = get_object(product, {'product':product}, products,
                                      Product)

                if 'note' in attributes:
                    note = attributes['note']
                notes = get_object(note, {'note':note}, notes, Note)
                inferences = get_object(cols[1], {'inference':cols[1]},
                                        inferences, Inference)

                if cols[7] == '.':
                    # tRNA gives '.' for phase,lets make it 9
                    cols[7] = 9

                features.append(
                    Features(
                        sample=sample,
                        contig=contigs[cols[0]],
                        cluster=clusters[cluster],
                        note=notes[note],
                        product=products[product],
                        inference=inferences[cols[1]],

                        start=int(cols[3]),
                        end=int(cols[4]),
                        is_positive=True if cols[6] == '+' else False,
                        is_tRNA=True if cols[2] == 'tRNA' else False,
                        is_rRNA=True if cols[2] == 'rRNA' else False,
                        phase=int(cols[7]),

                        prokka_id=prokka_id,
                        dna=genes[prokka_id] if prokka_id in genes else '',
                        aa=proteins[prokka_id] if prokka_id in proteins else '',
                    )
                )

    return features
