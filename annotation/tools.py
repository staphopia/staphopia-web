"""
Useful functions associated with gene.

To use:
from gene.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from annotation.models import Annotation, Inference, Feature
from staphopia.utils import timeit, gziplines, read_fasta, read_json


def insert_annotation(sample, version, files, force=False):
    """Insert the annotation to the database."""
    if force:
        delete_annotation(sample, version)

    aa = read_fasta(files['annotation_proteins'], compressed=True)
    dna = read_fasta(files['annotation_genes'], compressed=True)
    blast_results = read_blast([files['annotation_blastp_sprot'],
                                files['annotation_blastp_staph']])
    info, gene, protein, rna, blast = read_gff(files['annotation_gff'], aa,
                                               dna, blast_results)

    try:
        Annotation.objects.create(
            sample=sample,
            version=version,
            info=info,
            gene=gene,
            protein=protein,
            rna=rna,
            blast=blast
        )
    except IntegrityError as e:
        raise CommandError(f'{sample.name} Annotation save error: {e}')


@transaction.atomic
def delete_annotation(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying annotation related results.')
    Annotation.objects.filter(sample=sample, version=version).delete()


@transaction.atomic
def insert_features(features):
    """Bulk insert a list of features."""
    Features.objects.bulk_create(features, batch_size=500)


def get_inferences():
    """Get the total list of inferences."""
    rows = {}
    for tag in Inference.objects.filter():
        key = f'{tag.inference}|{tag.product}|{tag.note}|{tag.name}'
        rows[key] = tag
    return rows


def get_features():
    """Get the total list of inferences."""
    rows = {}
    for tag in Feature.objects.filter():
        rows[tag.feature] = tag
    return rows


def read_blast(files, compressed=True):
    results = {}
    for file in files:
        json_data = read_json(file, compressed=compressed)
        for entry in json_data['BlastOutput2']:
            hit = entry['report']['results']['search']
            if len(hit['hits']):
                # Only storing the top hit
                hsp = hit['hits'][0]['hsps'][0]
                mismatch = hsp['align_len'] - hsp['identity']
                hd = mismatch
                if hit['query_len'] > hsp['align_len']:
                    # Include those bases that weren't aligned
                    hd = hit['query_len'] - hsp['align_len'] + mismatch

                results[hit['query_title']] = {
                    'bitscore': int(hsp['bit_score']),
                    'evalue': hsp['evalue'],
                    'identity': hsp['identity'],
                    'mismatch': mismatch,
                    'gaps': hsp['gaps'],
                    'hamming_distance': hd,
                    'query_from': hsp['query_from'],
                    'query_to': hsp['query_to'],
                    'query_len': hit['query_len'],
                    'hit_from': hsp['hit_from'],
                    'hit_to': hsp['hit_to'],
                    'align_len': hsp['align_len'],
                    'qseq': hsp['qseq'],
                    'hseq': hsp['hseq'],
                    'midline': hsp['midline']
                }
            else:
                if hit['query_title'] not in results:
                    results[hit['query_title']] = {'message': 'No hits found'}

    return results


@timeit
def read_gff(gff, aa, dna, blast_results):
    """Read through the GFF and extract annotations."""
    info = {}
    rna = {}
    gene = {}
    protein = {}
    blast = {}
    features = get_features()
    inferences = get_inferences()

    done_reading = False

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
            feature = cols[2]
            if not feature == 'gene':
                # Parse attributes
                if feature not in features:
                    obj = Feature.objects.create(feature=feature)
                    features[feature] = obj
                attributes = dict(a.split('=') for a in cols[8].split(';'))
                locus_tag = attributes['locus_tag']
                inference = feature
                product = 'none'
                note = 'none'
                name = 'none'
                is_rna = False

                if 'RNA' in feature:
                    is_rna = True
                    rna[locus_tag] = dna[locus_tag]
                else:
                    gene[locus_tag] = dna[locus_tag]
                    protein[locus_tag] = aa[locus_tag]

                if 'query_title' in attributes:
                    if attributes['query_title'] not in blast_results:
                        blast[locus_tag] = blast_results[attributes['query_title']]
                    else:
                        blast[locus_tag] = {'message': 'No hits found'}
                else:
                    blast[locus_tag] = {'message': 'blast not applicable'}

                if 'inference' in attributes:
                    if 'RefSeq' in attributes['inference']:
                        inference = attributes['inference'].split('RefSeq:')[1]
                    elif feature == 'CDS':
                        inference = 'hypothetical'

                if product in attributes:
                    product = attributes['product']
                if note in attributes:
                    note = attributes['note']
                if name in attributes:
                    name = attributes['name']

                inference_key = f'{inference}|{product}|{note}|{name}'
                if inference_key in inferences:
                    inference = inferences[inference_key]
                else:
                    inference = Inference.objects.create(
                        inference=inference,
                        product=product,
                        note=note,
                        name=name
                    )
                    inferences[inference_key] = inference

                if cols[7] == '.':
                    # tRNA gives '.' for phase,lets make it 9
                    cols[7] = 9

                info[locus_tag] = {
                    'contig': cols[0].split('_')[1],
                    'start': int(cols[3]),
                    'end': int(cols[4]),
                    'strand': 1 if cols[6] == '+' else -1,
                    'phase': int(cols[7]),
                    'type': 'RNA' if is_rna else feature,
                    feature: True,
                    'inference': inference.id,
                }

    return [info, gene, protein, rna, blast]
