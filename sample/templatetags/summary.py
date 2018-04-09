from collections import OrderedDict
import json

from django import template
from django.db import connection
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from ena.models import CenterNames, Experiment
from sample.models import Sample
from assembly.models import Summary

from api.queries.assemblies import get_assembly_stats
from api.queries.samples import get_sample_metadata, get_samples
from api.queries.sequences import get_sequencing_stats

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def query_database(sql):
    """Submit SQL query to the database."""
    cursor = connection.cursor()
    cursor.execute(sql)
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def get_ena_link(accession):
    return (
        '<a href="http://www.ebi.ac.uk/ena/data/view/{0}" target="_blank"'
            'title="View {0} in another window.">'
        '{0}</a>'.format(accession)
    )


@register.simple_tag(takes_context=True)
@register.filter(needs_autoescape=True)
def get_metadata(context, sample_id):
    user_id = context['request'].user.pk if context['request'].user.pk else 2
    user = User.objects.get(pk=user_id)

    metadata = get_sample_metadata([sample_id], user_id)[0]
    sample = get_samples(user_id, sample_id=sample_id)[0]
    stats = {}
    stats['username'] = user.username
    stats['is_public'] = metadata['is_public']
    stats['is_published'] = metadata['is_published']
    stats['sample_name'] = sample['name']
    stats['sample'] = OrderedDict((
        ('Scientific Name', metadata['biosample_scientific_name']),
        ('Strain', metadata['strain']),
        ('Collection Date', metadata['collection_date']),
        ('Country', metadata['country']),
        ('Region', metadata['region']),
        ('Isolate', metadata['isolate']),
        ('Isolation Source', metadata['isolation_source']),
        ('Serotype', metadata['serotype']),
        ('Serovar', metadata['serovar']),
        ('Host', metadata['host']),
        ('Host Status', metadata['host_status']),
        ('Host Sex', metadata['host_sex']),
        ('Host Body Site', metadata['host_body_site'])
    ))
    sequencing_center = (
        '<a href="{0}" target="_blank" title="View {1} in another window.">'
        '{1}</a>'.format(metadata['center_link'], metadata['center_name'])
    )

    stats['sequencing'] = OrderedDict((
        ('Sequencing Center', mark_safe(sequencing_center)),
        ('Instrument Model', metadata['instrument_model']),
        ('Library Layout', metadata['library_layout']),
        ('Library Strategy', metadata['library_strategy']),
        ('Library Selection', metadata['library_selection'])
    ))
    stats['center_link'] = metadata['center_link']
    if metadata['contains_ena_metadata']:
        stats['ena'] = OrderedDict((
            ('BioSample Accession',
             mark_safe(get_ena_link(metadata['sample_accession']))),
            ('Study Accession',
             mark_safe(get_ena_link(metadata['study_accession']))),
            ('Study Title', metadata['study_title']),
            ('Experiment Accession',
             mark_safe(get_ena_link(metadata['experiment_accession']))),
            ('Experiment Title', metadata['experiment_title']),
            ('First Public', metadata['first_public'])
        ))
    else:
        stats['ena'] = False

    return stats


@register.simple_tag
def get_publications(sample_id):
    return query_database(
        """
        SELECT sample_id, pmid
        FROM sample_topublication AS s
        LEFT JOIN sample_publication AS p
        ON s.publication_id=p.id
        WHERE s.sample_id={0};
        """.format(sample_id)
    )


@register.simple_tag
def get_mlst(sample_id):
    stats = {}
    stats['srst2_hits'] = []
    stats['srst2_stats'] = []

    stats['blast'] = []
    row = query_database(
        """
        SELECT m.sample_id, st, m.ariba, m.mentalist, m.blast,
               r.ariba AS ariba_report, r.mentalist AS mentalist_report,
               r.blast AS blast_report
        FROM mlst_mlst AS m
        LEFT JOIN mlst_report AS r
        ON m.sample_id=r.sample_id
        WHERE m.sample_id={0};
        """.format(sample_id)
    )[0]
    stats['st'] = [
        row['st'] if int(row['st']) else '-',
        row['ariba'] if int(row['ariba']) else '-',
        row['mentalist'] if int(row['mentalist']) else '-',
        row['blast'] if int(row['blast']) else '-'
    ]
    stats['ariba'] = []
    if row['ariba']:
        for result in row['ariba_report']:
            stats['ariba'].append([
                result['gene'], result['allele'], result['cov'], result['pc'],
                result['ctgs'], result['depth'], result['hetmin'],
                result['hets']
            ])

    for loci, blast in row['blast_report'].items():
        coverage = "{0:.1f}".format(
            float(blast['slen']) / float(blast['length']) * 100
        )
        stats['blast'].append([
            loci, blast['sseqid'].split('.')[1], blast['evalue'],
            blast['bitscore'], coverage,
            "{0:.1f}".format(float(blast['pident'])), blast['gaps'],
            blast['mismatch']
        ])

    return stats


@register.simple_tag
def get_taxon_id(sample_id):
    exp = Experiment.objects.get(experiment_accession=sample_id)
    return exp.tax_id


@register.simple_tag
def get_center_name(center_name):
    try:
        center = CenterNames.objects.get(ena_name=center_name)
        return center.name
    except CenterNames.DoesNotExist:
        return '-'


def sort_keys_by_int(dictionary):
    return sorted((int(key), value) for key, value in dictionary.items())


@register.simple_tag(takes_context=True)
def get_sequence_quality(context, sample_id):
    user_id = context['request'].user.pk if context['request'].user.pk else 2
    stats = {}
    per_base = {}
    first = True
    for row in get_sequencing_stats([sample_id], user_id, qual_per_base=True):
        if row['name'] in ['cleanup', 'original']:
            stats[row['name']] = OrderedDict((
                ('Estimated Coverage', "{0:.2f}x".format(row['coverage'])),
                ('Average Quality', "Q{0:.2f}".format(row['qual_mean'])),
                ('Total Base Count', "{0:,} bp".format(row['total_bp'])),
                ('Total Read Count', "{0:,}".format(row['read_total'])),
                ('Mean Read Length', int(row['read_mean'])),
                ('Minimum Read Length', int(row['read_min'])),
                ('Maximum Read Length', int(row['read_max']))
            ))
            for key, val in json.loads(row['qual_per_base']).items():
                if first:
                    per_base[int(key)] = [val]
                else:
                    per_base[int(key)].append(val)
            first = False

    stats['per_base'] = sort_keys_by_int(per_base)
    return stats


@register.simple_tag(takes_context=True)
def get_assembly(context, sample_id):
    user_id = context['request'].user.pk if context['request'].user.pk else 2
    row = get_assembly_stats([sample_id], user_id)[0]

    stats = OrderedDict((
        ('Total Contigs', "{0:,}".format(row['total_contig'])),
        ('Total Assembled Length',
         "{0:,} bp".format(row['total_contig_length'])),
        ('N50 Length',"{0:,} bp".format(row['n50_contig_length'])),
        ('GC Content', "{0:.2f} %)".format(
            row['contig_percent_g'] + row['contig_percent_c']
        )),
        ('Maximum Contig Length',
         "{0:,} bp".format(row['max_contig_length'])),
        ('Mean Contig Length',
         "{0:,} bp".format(int(row['mean_contig_length']))),
        ('Median Contig Length',
         "{0:,} bp".format(row['median_contig_length'])),
        ('Minimum Contig Length',
         "{0:,} bp".format(row['min_contig_length'])),
        ('Contigs >= 1Mb (%)', "{0:,} ({1:.2f} %)".format(
            row['contigs_greater_1m'], row['percent_contigs_greater_1m']
        )),
        ('Contigs >= 100Kb (%)', "{0:,} ({1:.2f} %)".format(
            row['contigs_greater_100k'],
            row['percent_contigs_greater_100k']
        )),
        ('Contigs >= 10Kb (%)', "{0:,} ({1:.2f} %)".format(
            row['contigs_greater_10k'],
            row['percent_contigs_greater_10k']
        )),
        ('Contigs >= 1Kb (%)', "{0:,} ({1:.2f} %)".format(
            row['contigs_greater_1k'], row['percent_contigs_greater_1k']
        )),
    ))

    return stats
