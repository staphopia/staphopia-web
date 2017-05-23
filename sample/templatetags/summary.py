from collections import OrderedDict
import json

from django import template
from django.db import connection
from django.contrib.auth.models import User

from ena.models import CenterNames, Experiment
from sample.models import Sample
from assembly.models import Stats
from mlst.models import Srst2

register = template.Library()


def query_database(sql):
    """Submit SQL query to the database."""
    cursor = connection.cursor()
    cursor.execute(sql)
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


@register.assignment_tag(takes_context=True)
def get_meta_data(context, sample_id):
    sample = Sample.objects.get(id=sample_id)
    owner = User.objects.get(id=sample.user_id)
    metadata = {'username': owner.username}
    if owner.username == 'ena':
        metadata = query_database(
            """SELECT s.is_paired, s.is_public, s.is_published, s.md5sum,
                      s.user_id, s.sample_tag, e.study_accession,
                      e.study_title, e.study_alias,
                      e.secondary_study_accession, e.sample_accession,
                      e.secondary_sample_accession, e.submission_accession,
                      e.experiment_accession, e.experiment_title,
                      e.experiment_alias, e.tax_id, e.scientific_name,
                      e.instrument_platform, e.instrument_model,
                      e.library_layout, e.library_strategy,
                      e.library_selection, e.center_name, e.center_link,
                      e.first_public, e.sample_id, e.broker_name, e.cell_line,
                      e.checklist, e.collected_by, e.collection_date,
                      e.country, e.description, e.environment_biome,
                      e.environment_feature, e.environment_material,
                      e.environmental_sample, e.germline, e.host,
                      e.host_body_site, e.host_sex, e.host_status,
                      e.host_tax_id, e.investigation_type, e.isolate,
                      e.isolation_source, e.location, e.project_name,
                      e.sample_alias, e.sequencing_method,e.serotype,
                      e.serovar, e.sex, e.strain, e.sub_species,
                      e.submitted_host_sex, e.submitted_sex, e.tissue_type,
                      e.biosample_center_name, e.biosample_first_public,
                      e.biosample_scientific_name, e.biosample_tax_id
               FROM sample_sample AS s
               LEFT JOIN sample_metadata AS e
               ON s.id=e.sample_id
               WHERE s.id={0}""".format(sample_id)
         )[0]
        metadata['username'] = owner.username
    return metadata


@register.assignment_tag
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


@register.assignment_tag(takes_context=True)
def get_mlst_data(context, sample):
    mlst = Srst2.objects.get(sample=sample)
    return mlst


@register.assignment_tag
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



@register.assignment_tag
def get_sequence_quality(sample_id):
    quality = query_database(
        """
        SELECT * FROM sequence_stat
        WHERE sample_id={0}
        ORDER BY is_original DESC
        """.format(sample_id)
    )

    # Convert JSON output to OrderedDict
    per_base = {}
    for key, val in json.loads(quality[0]['qual_per_base']).items():
        per_base[int(key)] = [val]

    for key, val in json.loads(quality[1]['qual_per_base']).items():
        per_base[int(key)].append(val)

    quality.append(sort_keys_by_int(per_base))
    return quality


@register.assignment_tag
def get_assembly_stats(sample_id):
    assembly = Stats.objects.get(sample_id=sample_id, is_scaffolds=False,
                                 is_plasmids=False)
    assembly.gc = assembly.contig_percent_g + assembly.contig_percent_c
    return assembly
