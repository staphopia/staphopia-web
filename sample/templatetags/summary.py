from collections import OrderedDict
import json

from django import template
from django.db import connection
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from ena.models import CenterNames, Experiment
from sample.models import Sample
from assembly.models import Stats
from mlst.models import Srst2

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
def get_meta_data(context, sample_id):
    user_id = context['request'].user.pk if context['request'].user.pk else 0
    cols = [
        'm.sample_id', 's.is_paired', 's.is_public', 's.is_published',
        's.sample_tag', 'u.username', 'm.contains_ena_metadata',
        'm.study_accession', 'm.study_title', 'm.study_alias',
        'm.secondary_study_accession', 'm.sample_accession',
        'm.secondary_sample_accession', 'm.submission_accession',
        'm.experiment_accession', 'm.experiment_title', 'm.experiment_alias',
        'm.tax_id', 'm.scientific_name', 'm.instrument_platform',
        'm.instrument_model', 'm.library_layout', 'm.library_strategy',
        'm.library_selection', 'm.center_name', 'm.center_link',
        'm.collected_by', 'm.location', 'm.country', 'm.region',
        'm.coordinates', 'm.description', 'm.environmental_sample',
        'm.biosample_first_public', 'm.isolate', 'm.isolation_source',
        'm.serotype', 'm.serovar', 'm.strain', 'm.sub_species',
        'm.biosample_scientific_name', 'm.sample_alias',
        'm.checklist', 'm.biosample_center_name', 'm.environment_biome',
        'm.environment_feature', 'm.environment_material', 'm.project_name',
        'm.host', 'm.host_status', 'm.host_sex', 'm.submitted_host_sex',
        'm.host_body_site', 'm.investigation_type', 'm.sequencing_method',
        'm.broker_name', 'm.first_public', 'm.collection_date']

    metadata = query_database("""SELECT {0}
             FROM sample_sample AS s
             LEFT JOIN sample_metadata AS m
             ON s.id=m.sample_id
             LEFT JOIN auth_user AS u
             ON s.user_id=u.id
             WHERE s.id={1} AND (s.is_public=TRUE OR s.user_id={2});""".format(
        ",".join(cols), sample_id, user_id
    ))[0]

    stats = {}
    stats['username'] = metadata['username']
    stats['is_public'] = metadata['is_public']
    stats['is_paired'] = metadata['is_paired']
    stats['is_published'] = metadata['is_published']
    stats['sample_tag'] = metadata['sample_tag']
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
def get_mlst_data(sample_id):
    stats = {}
    srst2 = query_database(
        """
        SELECT st_original, st_stripped, is_exact, arcc, aroe, glpf, gmk, pta,
               tpi, yqil, mismatches, depth, "maxMAF"
        FROM mlst_srst2
        WHERE sample_id={0};
        """.format(sample_id)
    )
    for row in srst2:
        stats['srst2_hits'] = OrderedDict((
            ('arcC', row['arcc']),
            ('aroE', row['aroe']),
            ('glpF', row['glpf']),
            ('gmk', row['gmk']),
            ('pta', row['pta']),
            ('tpi', row['tpi']),
            ('yqiL', row['yqil'])
        ))
        stats['srst2_stats'] = OrderedDict((
            ('Mismatches', row['mismatches']),
            ('Depth', "{0:.2f}".format(row['depth'])),
            ('Maximum MAF', "{0:.4f}".format(row['maxMAF']))
        ))

    stats['blast'] = []
    blast = query_database(
        """
        SELECT locus_name, locus_id, bitscore, slen, length, gaps, mismatch,
               pident, evalue
        FROM mlst_blast
        WHERE sample_id={0}
        ORDER BY locus_name ASC
        LIMIT 7;
        """.format(sample_id)
    )

    for row in blast:
        coverage = "{0:.2f}".format(float(row['slen']) / row['length'] * 100)
        stats['blast'].append([
            row['locus_name'], row['locus_id'], row['evalue'], row['bitscore'],
            coverage, row['pident'], row['gaps'], row['mismatch']
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


@register.simple_tag
def get_sequence_quality(sample_id):
    stats = {}
    quality = query_database(
        """
        SELECT is_original, coverage, qual_mean, total_bp, read_total,
               read_mean, read_min, read_max, qual_per_base
        FROM sequence_stat
        WHERE sample_id={0}
        ORDER BY is_original DESC
        """.format(sample_id)
    )

    for row in quality:
        key = 'original' if row['is_original'] else 'processed'
        stats[key] = OrderedDict((
            ('Estimated Coverage', "{0:.2f}x".format(row['coverage'])),
            ('Average Quality', "Q{0:.2f}".format(row['qual_mean'])),
            ('Total Base Count', "{0:,} bp".format(row['total_bp'])),
            ('Total Read Count', "{0:,}".format(row['read_total'])),
            ('Mean Read Length', int(row['read_mean'])),
            ('Minimum Read Length', int(row['read_min'])),
            ('Maximum Read Length', int(row['read_max']))
        ))

    # Convert JSON output to OrderedDict
    per_base = {}
    for key, val in json.loads(quality[0]['qual_per_base']).items():
        per_base[int(key)] = [val]

    for key, val in json.loads(quality[1]['qual_per_base']).items():
        per_base[int(key)].append(val)

    stats['per_base'] = sort_keys_by_int(per_base)
    return stats


@register.simple_tag
def get_assembly_stats(sample_id):
    row = query_database(
        """
        SELECT total_contig, total_contig_length, min_contig_length,
               median_contig_length, mean_contig_length, max_contig_length,
               n50_contig_length, contigs_greater_1k, contigs_greater_10k,
               contigs_greater_100k, contigs_greater_1m,
               percent_contigs_greater_1k, percent_contigs_greater_10k,
               percent_contigs_greater_100k, percent_contigs_greater_1m,
               contig_percent_g, contig_percent_c
        FROM assembly_stats
        WHERE sample_id={0} AND is_scaffolds=FALSE AND is_plasmids=FALSE;
        """.format(sample_id)
    )

    stats = OrderedDict((
        ('Total Contigs', "{0:,}".format(row[0]['total_contig'])),
        ('Total Assembled Length',
         "{0:,} bp".format(row[0]['total_contig_length'])),
        ('N50 Length',"{0:,} bp".format(row[0]['n50_contig_length'])),
        ('GC Content', "{0:.2f} %)".format(
            row[0]['contig_percent_g'] + row[0]['contig_percent_c']
        )),
        ('Maximum Contig Length',
         "{0:,} bp".format(row[0]['max_contig_length'])),
        ('Mean Contig Length',
         "{0:,} bp".format(int(row[0]['mean_contig_length']))),
        ('Median Contig Length',
         "{0:,} bp".format(row[0]['median_contig_length'])),
        ('Minimum Contig Length',
         "{0:,} bp".format(row[0]['min_contig_length'])),
        ('Contigs >= 1Mb (%)', "{0:,} ({1:.2f} %)".format(
            row[0]['contigs_greater_1m'], row[0]['percent_contigs_greater_1m']
        )),
        ('Contigs >= 100Kb (%)', "{0:,} ({1:.2f} %)".format(
            row[0]['contigs_greater_100k'],
            row[0]['percent_contigs_greater_100k']
        )),
        ('Contigs >= 10Kb (%)', "{0:,} ({1:.2f} %)".format(
            row[0]['contigs_greater_10k'],
            row[0]['percent_contigs_greater_10k']
        )),
        ('Contigs >= 1Kb (%)', "{0:,} ({1:.2f} %)".format(
            row[0]['contigs_greater_1k'], row[0]['percent_contigs_greater_1k']
        )),
    ))

    return stats
