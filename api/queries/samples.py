"""API utilities for sample related viewsets."""
from api.utils import query_database


def get_samples(user_id, sample_id=None, sample_ids=None, user_only=False):
    """Return samples."""
    sql = None
    if user_only:
        sql = """SELECT s.id AS sample_id, s.is_paired, s.is_public,
                        s.is_published, s.sample_tag, m.st_original,
                        m.st_stripped, m.is_exact AS st_is_exact_match
                 FROM sample_sample as s
                 LEFT JOIN mlst_srst2 as m
                 ON s.id = m.sample_id
                 WHERE s.user_id={0}
                 ORDER BY s.id DESC""".format(user_id)
    elif sample_id:
        sql = """SELECT s.id AS sample_id, s.is_paired, s.is_public,
                        s.is_published, s.sample_tag, m.st_original,
                        m.st_stripped, m.is_exact AS st_is_exact_match
                 FROM sample_sample as s
                 LEFT JOIN mlst_srst2 as m
                 ON s.id = m.sample_id
                 WHERE s.id={0}
                       AND (s.is_public=TRUE OR s.user_id={1})""".format(
            sample_id,
            user_id
        )
    elif sample_ids:
        sql = """SELECT s.id AS sample_id, s.is_paired, s.is_public,
                        s.is_published, s.sample_tag, m.st_original,
                        m.st_stripped, m.is_exact AS st_is_exact_match
                 FROM sample_sample as s
                 LEFT JOIN mlst_srst2 as m
                 ON s.id = m.sample_id
                 WHERE s.id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
                 ORDER BY s.id""".format(
            ','.join([str(i) for i in sample_ids]),
            user_id
        )
    else:
        sql = """SELECT s.id AS sample_id, s.is_paired, s.is_public,
                        s.is_published, s.sample_tag, m.st_original,
                        m.st_stripped, m.is_exact AS st_is_exact_match
                 FROM sample_sample as s
                 LEFT JOIN mlst_srst2 as m
                 ON s.id = m.sample_id
                 WHERE s.is_public=TRUE OR s.user_id={0}""".format(user_id)

    return query_database(sql)


def get_samples_by_tag(tag_id):
    """Return samples associated with a tag."""
    sql = """SELECT t.sample_id, s.sample_tag,
                    s.is_paired, s.is_public, s.is_published,
                    m.st_original, m.st_stripped,
                    m.is_exact AS st_is_exact_match
             FROM sample_totag AS t
             LEFT JOIN sample_sample AS s
             ON t.sample_id=s.id
             LEFT JOIN mlst_srst2 as m
             ON m.sample_id=s.id
             WHERE t.tag_id={0}
             ORDER BY s.sample_tag ASC;""".format(tag_id)
    return query_database(sql)


def get_public_samples(is_published=False):
    """Return sample info associated with a tag."""
    sql = None
    if is_published:
        sql = 'SELECT * FROM published_ena_samples;'
        results = {}
        for row in query_database(sql):
            if row['sample_tag'] not in results:
                results[row['sample_tag']] = row
                if row['pmid']:
                    results[row['sample_tag']]['pmid'] = [int(row['pmid'])]
                else:
                    results[row['sample_tag']]['pmid'] = []
            else:
                if row['pmid']:
                    results[row['sample_tag']]['pmid'].append(int(row['pmid']))

        return [vals for k, vals in results.items()]

    else:
        return query_database('SELECT * FROM public_ena_samples;')


def get_resistance_by_samples(sample_ids, resistance_id=None):
    """Return snps associated with a sample."""
    optional = ""
    if resistance_id:
        optional = "AND resistance_id={0}".format(resistance_id)
    sql = """SELECT sample_id, value as mic, phenotype
             FROM sample_toresistance
             WHERE sample_id IN ({0}) {1};""".format(
        ','.join([str(i) for i in sample_ids]), optional
    )

    return query_database(sql)


def get_tags_by_sample(sample_id, user_id):
    """Return tags associated with a sample."""
    sql = """SELECT s.sample_id, s.tag_id, t.tag, t.comment
             FROM sample_totag AS s
             LEFT JOIN sample_tag AS t
             ON s.tag_id=t.id
             LEFT JOIN sample_sample AS a
             ON s.sample_id=a.id
             WHERE s.sample_id={0}
                   AND (a.is_public=TRUE OR a.user_id={1});""".format(
        sample_id,
        user_id
    )
    return query_database(sql)


def get_sample_metadata(sample_id, single=True):
    """Return metadata associated with a sample."""
    cols = [
        'sample_id', 'contains_ena_metadata', 'study_accession', 'study_title',
        'study_alias', 'secondary_study_accession', 'sample_accession',
        'secondary_sample_accession', 'submission_accession',
        'experiment_accession', 'experiment_title', 'experiment_alias',
        'tax_id', 'scientific_name', 'instrument_platform', 'instrument_model',
        'library_layout', 'library_strategy', 'library_selection',
        'center_name', 'center_link', 'first_public', 'cell_line',
        'collected_by', 'collection_date', 'country', 'description',
        'environmental_sample', 'biosample_first_public', 'germline',
        'isolate', 'isolation_source', 'location', 'serotype', 'serovar',
        'sex', 'submitted_sex', 'strain', 'sub_species', 'tissue_type',
        'biosample_tax_id', 'biosample_scientific_name', 'sample_alias',
        'checklist', 'biosample_center_name', 'environment_biome',
        'environment_feature', 'environment_material', 'project_name', 'host',
        'host_tax_id', 'host_status', 'host_sex', 'submitted_host_sex',
        'host_body_site', 'investigation_type', 'sequencing_method',
        'broker_name'
    ]
    sql = None
    if single:
        sql = """SELECT {0} FROM sample_metadata
                 WHERE sample_id={1};""".format(','.join(cols), sample_id)
    else:
        sql = """SELECT {0} FROM sample_metadata
                 WHERE sample_id IN ({1})
                 ORDER BY sample_id;""".format(
            ','.join(cols),
            ','.join([str(i) for i in sample_id])
        )

    return query_database(sql)
