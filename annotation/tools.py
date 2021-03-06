"""
Useful functions associated with gene.

To use:
from gene.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from annotation.models import Annotation, Inference, Feature, Repeat
from staphopia.utils import timeit, gziplines, read_fasta, read_json


def insert_annotation(sample, version, files, force=False):
    """Insert the annotation to the database."""
    if force:
        delete_annotation(sample, version)

    amino_acid = read_fasta(files['annotation_proteins'], compressed=True)
    dna = read_fasta(files['annotation_genes'], compressed=True)
    blast_results = read_blast([files['annotation_blastp_sprot'],
                                files['annotation_blastp_staph']])
    info, gene, protein, rna, blast, repeat = read_gff(
        files['annotation_gff'], amino_acid, dna, blast_results
    )

    try:
        print(f'{sample.name}: Inserting annotation')
        Annotation.objects.create(
            sample=sample,
            version=version,
            info=info,
            gene=gene,
            protein=protein,
            rna=rna,
            blast=blast
        )
        if repeat:
            Repeat.objects.create(
                sample=sample,
                version=version,
                repeat=repeat
            )
    except IntegrityError as exception:
        raise CommandError(f'{sample.name} Annotation save error: {exception}')


@transaction.atomic
def delete_annotation(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying annotation related results.')
    Annotation.objects.filter(sample=sample, version=version).delete()
    Repeat.objects.filter(sample=sample, version=version).delete()


@transaction.atomic
def create_inference(inference, product, note, name):
    """Get or create annotation inference."""
    inference = Inference.objects.get_or_create(
        inference=inference,
        product=product,
        note=note,
        name=name
    )
    return inference[0]


def get_inferences():
    """Get the total list of inferences."""
    rows = {}
    for tag in Inference.objects.filter():
        # Assume inference is unique RefSeq accession
        key = f'{tag.inference}'

        if tag.inference == 'hypothetical' or tag.inference.endswith('RNA'):
            # Not a unique accession
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
    "Read blast results and return list."
    results = {}
    for file in files:
        json_data = read_json(file, compressed=compressed)
        for entry in json_data['BlastOutput2']:
            hit = entry['report']['results']['search']
            if hit['hits']:
                # Only storing the top hit
                hsp = hit['hits'][0]['hsps'][0]
                mismatch = hsp['align_len'] - hsp['identity']
                distance = mismatch
                if hit['query_len'] > hsp['align_len']:
                    # Include those bases that weren't aligned
                    distance = hit['query_len'] - hsp['align_len'] + mismatch

                results[hit['query_title']] = {
                    'bitscore': int(hsp['bit_score']),
                    'evalue': hsp['evalue'],
                    'identity': hsp['identity'],
                    'mismatch': mismatch,
                    'gaps': hsp['gaps'],
                    'hamming_distance': distance,
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
def read_gff(gff, amino_acid, dna, blast_results):
    """Read through the GFF and extract annotations."""
    info = []
    rna = {}
    gene = {}
    protein = {}
    blast = []
    repeat = []
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
                if feature == 'repeat_region':
                    repeat.append({
                        'contig': cols[0],
                        'source': cols[1],
                        'type': cols[2],
                        'start': int(cols[3]),
                        'end': int(cols[4]),
                        'score': cols[5],
                        'strand': cols[6],
                        'phase': cols[7],
                        'note': attributes['note'],
                        'family': attributes['rpt_family'],
                        'rpt_type': attributes['rpt_type']
                    })
                else:
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
                        protein[locus_tag] = amino_acid[locus_tag]

                    if 'query_title' in attributes:
                        if attributes['query_title'] not in blast_results:
                            results = blast_results[attributes['query_title']]
                            results['locus_tag'] = locus_tag
                            blast.append(results)
                        else:
                            blast.append({
                                'locus_tag': locus_tag,
                                'message': 'No hits found'
                            })
                    else:
                        blast.append({
                            'locus_tag': locus_tag,
                            'message': 'BLAST not applicable'
                        })

                    if 'inference' in attributes:
                        if 'RefSeq' in attributes['inference']:
                            inference = attributes['inference'].split(
                                'RefSeq:'
                            )[1]
                        elif feature == 'CDS':
                            inference = 'hypothetical'

                    if 'product' in attributes:
                        product = attributes['product']
                    if 'note' in attributes:
                        note = attributes['note']
                    if 'Name' in attributes:
                        name = attributes['Name']
                        if '_' in name:
                            name = name.split('_')[0]

                    inference_key = f'{inference}'
                    if inference == 'hypothetical':
                        inference_key = f'{inference}|{product}|{note}|{name}'
                    elif inference.endswith('RNA'):
                        inference_key = f'{inference}|{product}|{note}|{name}'

                    if inference_key not in inferences:
                        inferences[inference_key] = create_inference(
                            inference, product, note, name
                        )
                    inference = inferences[inference_key]
                    if cols[7] == '.':
                        # tRNA gives '.' for phase,lets make it 9
                        cols[7] = 9

                    info.append({
                        'contig': cols[0].split('_')[1],
                        'locus_tag': locus_tag,
                        'start': int(cols[3]),
                        'end': int(cols[4]),
                        'strand': 1 if cols[6] == '+' else -1,
                        'phase': int(cols[7]),
                        'type': 'RNA' if is_rna else feature,
                        feature: True,
                        'inference': inference.id,
                    })

    return [info, gene, protein, rna, blast, repeat]
