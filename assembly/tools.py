"""
Useful functions associated with assembly.

To use:
from assembly.tools import UTIL1, UTIL2, etc...
"""
import json
import numpy

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_fasta, read_json, timeit
from assembly.models import Contig, Sequence, Summary

GENOME_SIZE = 2814816


@timeit
def contig_lengths(contigs):
    return {
        '100k': sum(i > 100000 for i in contigs),
        '10k': sum(i > 10000 for i in contigs),
        '1k': sum(i > 1000 for i in contigs),
        '1m': sum(i > 1000000 for i in contigs)
    }


@timeit
def nucleotide_counts(contigs, total_bp):
    c = {'a': 0, 'c': 0, 'g': 0, 't': 0, 'n': 0, 'total_non_acgtn': 0}
    for contig in contigs:
        for n in contig.lower():
            if n not in ['a', 'c', 'g', 't', 'n']:
                c['total_non_acgtn'] += 1
            else:
                c[n] += 1

    c['non_acgtn'] = c['total_non_acgtn'] / total_bp
    c['a'] = c['a'] / total_bp
    c['c'] = c['c'] / total_bp
    c['g'] = c['g'] / total_bp
    c['n'] = c['n'] / total_bp
    c['t'] = c['t'] / total_bp
    return c


@timeit
def calculate_n50(contigs, genome_size, assembly_size):
    stats = {'n50': 0, 'ng50': 0, 'l50': 0, 'lg50': 0}
    total = 0
    total_contig = 0
    for contig in contigs:
        total += contig
        total_contig += 1
        if total >= genome_size:
            if not stats['ng50']:
                stats['ng50'] = contig
                stats['lg50'] = total_contig
        if total >= assembly_size:
            if not stats['n50']:
                stats['n50'] = contig
                stats['l50'] = total_contig

        if stats['n50'] and stats['ng50']:
            break

    return stats


def print_percent(val):
    return '{0:.2f}'.format(val * 100)


@timeit
def generate_assembly_stats(fasta):
    lengths = sorted([len(seq) for seq in fasta], key=int, reverse=True)
    length_totals = contig_lengths(lengths)
    total_contig = len(fasta)
    total_bp = sum(lengths)
    counts = nucleotide_counts(fasta, total_bp)
    n50 = calculate_n50(lengths, GENOME_SIZE//2, total_bp//2)
    np_array = numpy.array(lengths)
    return {
        "contig_non_acgtn": print_percent(counts['non_acgtn']),
        "contig_percent_a": print_percent(counts['a']),
        "contig_percent_c": print_percent(counts['c']),
        "contig_percent_g": print_percent(counts['g']),
        "contig_percent_n": print_percent(counts['n']),
        "contig_percent_t": print_percent(counts['t']),
        "contigs_greater_100k": length_totals['100k'],
        "contigs_greater_10k": length_totals['10k'],
        "contigs_greater_1k": length_totals['1k'],
        "contigs_greater_1m": length_totals['1m'],
        "l50_contig_count": n50['l50'],
        "lg50_contig_count": n50['lg50'],
        "max_contig_length": max(lengths),
        "mean_contig_length": int(numpy.mean(np_array)),
        "median_contig_length": int(numpy.median(np_array)),
        "min_contig_length": min(lengths),
        "n50_contig_length": n50['n50'],
        "ng50_contig_length": n50['ng50'],
        "num_contig_non_acgtn": counts['total_non_acgtn'],
        "percent_contigs_greater_100k": print_percent(
            length_totals['100k'] / total_contig
        ),
        "percent_contigs_greater_10k": print_percent(
            length_totals['10k'] / total_contig
        ),
        "percent_contigs_greater_1k": print_percent(
            length_totals['1k'] / total_contig
        ),
        "percent_contigs_greater_1m": print_percent(
            length_totals['1m'] / total_contig
        ),
        "total_contig": total_contig,
        "total_contig_length": total_bp
    }


@timeit
@transaction.atomic
def insert_assembly(sample, version, files, force=False):
    """Insert the assembled scaffolds to the database."""
    if force:
        delete_assembly(sample, version)

    assembly = read_fasta(files['assembly_contigs'], compressed=True)
    graph = read_fasta(files['assembly_graph'], compressed=True)

    # Get the PROKKA naming of contigs
    prokka_name = {}
    with open(files['annotation_contigs'], 'r') as fh:
        for line in fh:
            spades, prokka = line.rstrip().split('\t')
            prokka_name[spades] = prokka

    fasta = {}
    contig_objects = []
    for spades, sequence in assembly.items():
        # Example SPAdes name: NODE_37_length_341_cov_381.897727
        # Filter contigs less than 200bp (coincidentally, same filter used by
        # Prokka)
        if spades in prokka_name:
            cols = spades.split('_')
            staphopia = ''.join([
                f'{sample.id}|{sample.name}|{cols[1]} coverage={cols[5]} ',
                f'length={cols[3]} analysis_version={version.tag}'
            ])

            fasta[staphopia] = sequence
            prokka = prokka_name[spades]

            contig_objects.append(Contig(
                sample=sample,
                version=version,
                spades=spades,
                prokka=prokka,
                staphopia=staphopia
            ))

    try:
        Contig.objects.bulk_create(contig_objects, batch_size=500)
        print(f'{sample.name}: Assembled contig names saved.')
    except IntegrityError as e:
        raise CommandError(f'{sample.name} Contig Name Error: {e}')

    try:
        Sequence.objects.create(
            sample=sample,
            version=version,
            fasta=fasta,
            graph=graph
        )
    except IntegrityError as e:
        raise CommandError(f'{sample.name} Fasta save error: {e}')

    try:
        # Generate stats based on filtered contigs < 200bp
        stats = generate_assembly_stats(list(fasta.values()))
        Summary.objects.create(sample=sample, version=version, **stats)
    except IntegrityError as e:
        raise CommandError(' '.join([
            f'Unable to insert stats for {sample.name} ({sample.id}).',
            f'Please use --force to update stats. Error: {e}'
        ]))


def delete_assembly(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying assembly related results.')
    Contig.objects.filter(sample=sample, version=version).delete()
    Sequence.objects.filter(sample=sample, version=version).delete()
    Summary.objects.filter(sample=sample, version=version).delete()


def get_contig(soemthing):
    print('delete me')
