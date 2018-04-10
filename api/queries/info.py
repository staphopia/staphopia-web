"""API utilities for info related queries."""
from api.utils import query_database


def get_sequencing_stats_by_year(is_original=False):
    """Return sequencing stats by year sample was first public."""
    original = 'TRUE' if is_original else 'FALSE'
    sql = """SELECT * FROM sequencing_stats_by_year({0});""".format(original)
    return query_database(sql)


def get_cgmlst_patterns():
    """Return cgmlst patterns and counts of public samples."""
    loci = []
    for row in query_database("SELECT id, name FROM cgmlst_loci;"):
        loci.append(str(row['id']))

    sql = """SELECT mentalist
             FROM cgmlst_cgmlst AS m
             LEFT JOIN sample_basic AS s
             ON m.sample_id=s.sample_id
             WHERE s.sample_id > 0 USER_PERMISSION
             ORDER BY m.sample_id ASC;"""

    patterns = {}
    for row in query_database(sql):
        pattern = ':'.join([str(row['mentalist'][l]) for l in loci])
        if pattern not in patterns:
            patterns[pattern] = 1
        else:
            patterns[pattern] += 1

    results = []
    counts = {}
    for pattern, count in patterns.items():
        if count not in counts:
            counts[count] = 1
        else:
            counts[count] += 1

    results = []
    for total_samples, count in sorted(counts.items(), reverse=True):
        results.append({
            'samples_in_pattern': total_samples,
            'count': count,
            'total_samples': count * total_samples,
        })

    return results


def get_assembly_stats_by_year(is_scaffolds=False, is_plasmids=False):
    """Return metadata associated with a sample."""
    scaffold = 'TRUE' if is_scaffolds else 'FALSE'
    plasmid = 'TRUE' if is_plasmids else 'FALSE'
    sql = """SELECT * FROM assembly_stats_by_year({0}, {1});""".format(
        scaffold, plasmid
    )
    return query_database(sql)


def get_publication_links():
    """Return how publication links wer made."""
    sql = """SELECT s.name, e.sra_to_pubmed, e.publication_id
             FROM ena_topublication AS e
             LEFT JOIN sample_sample AS s
             ON e.experiment_accession=s.name
             WHERE s.is_flagged=FALSE AND s.is_published=TRUE;"""

    results = {
        'elink': 0,
        'text': 0
    }
    names = {'elink': {}, 'text': {}, 'all': {}}
    pmid = {'elink': {}, 'text': {}, 'all': {}}
    for row in query_database(sql):
        if row['sra_to_pubmed']:
            if row['name'] not in names['elink']:
                results['elink'] += 1
                names['elink'][row['name']] = True
            pmid['elink'][row['publication_id']] = True
        else:
            if row['name'] not in names['text']:
                results['text'] += 1
                names['text'][row['name']] = True
            pmid['text'][row['publication_id']] = True
        names['all'][row['name']] = True
        pmid['all'][row['publication_id']] = True

    results['elink_pmid'] = len(pmid['elink'])
    results['text_pmid'] = len(pmid['all']) - results['elink_pmid']
    results['total'] = len(names['all'])
    results['total_pmid'] = len(pmid['all'])

    return [results]


def get_submission_by_year(all_submissions=False):
    """Return the published submissions by year."""
    sql = None
    if all_submissions:
        sql = "SELECT * FROM submission_by_year;"
    else:
        sql = """SELECT metadata->'first_public' AS first_public,
                        s.is_published
                 FROM sample_metadata AS m
                 LEFT JOIN sample_basic AS s
                 ON m.sample_id=s.sample_id
                 WHERE s.sample_id > 0 USER_PERMISSION
                 ORDER BY first_public;"""

    results = []
    years = {}
    for row in query_database(sql):
        year = None
        if all_submissions:
            year = int(row['year'])
            row['is_published'] = False
        else:
            year = int(row['first_public'][0:4])

        if year not in years:
            years[year] = {'published': 0, 'unpublished': 0, 'total': 0}

        if row['is_published']:
            years[year]['published'] += 1
        else:
            years[year]['unpublished'] += 1

        if all_submissions:
            years[year]['published'] = 0
            years[year]['unpublished'] = 0
            years[year]['total'] = row['count']
        else:
            years[year]['total'] += 1

    overall = [0, 0, 0]
    for key, val in sorted(years.items()):
        overall[0] += val['published']
        overall[1] += val['unpublished']
        overall[2] += val['total']
        results.append({
            'year': key,
            'published': val['published'],
            'unpublished': val['unpublished'],
            'count': val['total'],
            'overall_published': overall[0],
            'overall_unpublished': overall[1],
            'overall': overall[2]
        })

    return results


def get_rank_by_year(is_original=False):
    """Return the published submissions by year."""
    results = []
    name = 'original' if is_original else 'cleanup'

    sql = """SELECT metadata->'first_public' AS first_public, rank
             FROM sample_metadata AS m
             LEFT JOIN sample_basic AS s
             ON m.sample_id=s.sample_id
             WHERE s.sample_id > 0 USER_PERMISSION
             ORDER BY first_public;""".format(
        name
    )

    years = {}
    overall = [0, 0, 0]
    for row in query_database(sql):
        year = int(row['first_public'][0:4])
        if year not in years:
            years[year] = {'bronze': 0, 'silver': 0, 'gold': 0, 'total': 0}

        if row['rank']:
            if row['rank'] == 1:
                years[year]['bronze'] += 1
            elif row['rank'] == 2:
                years[year]['silver'] += 1
            elif row['rank'] == 3:
                years[year]['gold'] += 1

            years[year]['total'] += 1

    overall = [0, 0, 0, 0]
    for key, val in sorted(years.items()):
        overall[0] += val['bronze']
        overall[1] += val['silver']
        overall[2] += val['gold']
        overall[3] += val['total']
        results.append({
            'year': key,
            'bronze': val['bronze'],
            'silver': val['silver'],
            'gold': val['gold'],
            'count': val['total'],
            'overall_bronze': overall[0],
            'overall_silver': overall[1],
            'overall_gold': overall[2],
            'overall': overall[3]
        })

    return results


def get_st_by_year():
    """Return the published submissions by year."""
    results = []
    sql = """SELECT metadata->'first_public' AS first_public, t.st,
                    predicted_novel, ariba, mentalist, blast, is_paired
             FROM sample_metadata AS m
             LEFT JOIN sample_basic AS s
             ON m.sample_id=s.sample_id
             LEFT JOIN mlst_mlst AS t
             ON m.sample_id=t.sample_id
             LEFT JOIN sequence_summary AS q
             ON m.sample_id=q.sample_id
             LEFT JOIN sequence_stage AS w
             ON w.id=q.stage_id
             WHERE w.name='cleanup' USER_PERMISSION
             ORDER BY first_public;"""

    years = {}
    types = set()
    for row in query_database(sql):
        year = int(row['first_public'][0:4])
        if year not in years:
            years[year] = {'unique': [], 'novel': [], 'assigned': 0,
                           'unassigned': 0, 'predicted_novel': 0,
                           'total': 0, 'all': 0, 'mentalist_blast': 0,
                           'mentalist_ariba': 0, 'ariba_blast': 0,
                           'mentalist': 0, 'ariba': 0, 'blast': 0,
                           'assigned_agree': 0, 'assigned_disagree': 0,
                           'unassigned_agree': 0, 'unassigned_disagree': 0}

        if row['is_paired']:
            if (row['ariba'] == row['blast']) and (
                    row['ariba'] == row['mentalist']):
                # All three programs agree
                if row['st']:
                    years[year]['assigned_agree'] += 1
                else:
                    years[year]['unassigned_agree'] += 1
            else:
                calls = []
                if row['ariba'] and row['ariba'] != 10000:
                    calls.append(row['ariba'])
                if row['blast']:
                    calls.append(row['blast'])
                if row['mentalist']:
                    calls.append(row['mentalist'])

                total_st = len(set(calls))
                if total_st == 1:
                    if row['st']:
                        years[year]['assigned_agree'] += 1
                    else:
                        if total_st:
                            if row['ariba'] and row['ariba'] != 10000:
                                # Ariba made a call with uncertainty, ST was
                                # not assigned
                                years[year]['unassigned_agree'] += 1
                            else:
                                years[year]['unassigned_disagree'] += 1
                        else:
                            years[year]['unassigned_agree'] += 1
                else:
                    if row['st']:
                        if total_st:
                            # Ariba made a call with uncertainty, so
                            # mentalist and/or BLAST were used to make call
                            if row['blast'] == row['mentalist']:
                                years[year]['assigned_agree'] += 1
                            elif row['blast'] and row['mentalist']:
                                years[year]['assigned_disagree'] += 1
                            else:
                                years[year]['assigned_agree'] += 1
                        else:
                            years[year]['assigned_disagree'] += 1
                    else:
                        if total_st:
                            years[year]['unassigned_disagree'] += 1
                        else:
                            years[year]['unassigned_agree'] += 1
        else:
            if row['blast'] == row['mentalist']:
                if row['st']:
                    years[year]['assigned_agree'] += 1
                else:
                    years[year]['unassigned_agree'] += 1
            else:
                if row['st']:
                    if row['blast'] and row['mentalist']:
                        # Mentalist and BLAST had two different calls
                        years[year]['assigned_disagree'] += 1
                    else:
                        # Either Mentalist or BLAST had a 0 call
                        years[year]['assigned_agree'] += 1

        if row['st']:
            if row['st'] not in types:
                years[year]['novel'].append(row['st'])
                types.add(row['st'])
            years[year]['unique'].append(row['st'])
            if row['is_paired']:
                if row['ariba'] == row['blast'] and (
                        row['mentalist'] == row['ariba']):
                    years[year]['all'] += 1
                elif row['ariba'] == row['blast'] and row['blast']:
                    years[year]['ariba_blast'] += 1
                elif row['ariba'] == row['mentalist'] and row['mentalist']:
                    years[year]['mentalist_ariba'] += 1
                elif row['mentalist'] == row['blast'] and row['mentalist']:
                    years[year]['mentalist_blast'] += 1
                elif row['ariba']:
                    years[year]['ariba'] += 1
                elif row['mentalist']:
                    years[year]['mentalist'] += 1
                elif row['blast']:
                    years[year]['blast'] += 1
            else:
                if row['mentalist'] == row['blast']:
                    years[year]['all'] += 1
                elif row['mentalist']:
                    years[year]['mentalist'] += 1
                elif row['blast']:
                    years[year]['blast'] += 1
            years[year]['assigned'] += 1
        else:
            if row['predicted_novel']:
                years[year]['predicted_novel'] += 1
            years[year]['unassigned'] += 1
        years[year]['total'] += 1

    overall = {
        'novel': 0, 'assigned': 0, 'unassigned': 0, 'predicted_novel': 0,
        'total': 0, 'all': 0, 'mentalist_blast': 0, 'mentalist_ariba': 0,
        'ariba_blast': 0, 'mentalist': 0, 'ariba': 0, 'blast': 0, 'partial': 0,
        'single': 0, 'assigned_agree': 0, 'assigned_disagree': 0,
        'unassigned_agree': 0, 'unassigned_disagree': 0,
    }
    for key, val in sorted(years.items()):
        single = val['mentalist'] + val['ariba'] + val['blast']
        partial = (
            val['mentalist_blast'] + val['mentalist_ariba'] +
            val['ariba_blast']
        )
        total_unique = len(list(set(val['unique'])))
        total_novel = len(list(set(val['novel'])))
        overall['total'] += val['total']
        overall['novel'] += total_novel
        overall['assigned'] += val['assigned']
        overall['assigned_agree'] += val['assigned_agree']
        overall['assigned_disagree'] += val['assigned_disagree']
        overall['unassigned'] += val['unassigned']
        overall['unassigned_agree'] += val['unassigned_agree']
        overall['unassigned_disagree'] += val['unassigned_disagree']
        overall['predicted_novel'] += val['predicted_novel']
        overall['all'] += val['all']
        overall['mentalist_blast'] += val['mentalist_blast']
        overall['mentalist_ariba'] += val['mentalist_ariba']
        overall['ariba_blast'] += val['ariba_blast']
        overall['mentalist'] += val['mentalist']
        overall['ariba'] += val['ariba']
        overall['blast'] += val['blast']
        overall['partial'] += partial
        overall['single'] += single
        results.append({
            'year': key,
            'unique': total_unique,
            'novel': total_novel,
            'assigned': val['assigned'],
            'assigned_agree': val['assigned_agree'],
            'assigned_disagree': val['assigned_disagree'],
            'unassigned': val['unassigned'],
            'unassigned_agree': val['unassigned_agree'],
            'unassigned_disagree': val['unassigned_disagree'],
            'predicted_novel': val['predicted_novel'],
            'all': val['all'],
            'partial': partial,
            'ariba_blast': val['ariba_blast'],
            'mentalist_blast': val['mentalist_blast'],
            'mentalist_ariba': val['mentalist_ariba'],
            'single': single,
            'ariba': val['ariba'],
            'mentalist': val['mentalist'],
            'blast': val['blast'],
            'count': val['total'],
            'overall_novel': overall['novel'],
            'overall_assigned': overall['assigned'],
            'overall_assigned_agree': overall['assigned_agree'],
            'overall_assigned_disagree': overall['assigned_disagree'],
            'overall_unassigned': overall['unassigned'],
            'overall_unassigned_agree': overall['unassigned_agree'],
            'overall_unassigned_disagree': overall['unassigned_disagree'],
            'overall_predicted_novel': overall['predicted_novel'],
            'overall_all': overall['all'],
            'overall_partial': overall['partial'],
            'overall_ariba_blast': overall['ariba_blast'],
            'overall_mentalist_blast': overall['mentalist_blast'],
            'overall_mentalist_ariba': overall['mentalist_ariba'],
            'overall_single': overall['single'],
            'overall_ariba': overall['ariba'],
            'overall_mentalist': overall['mentalist'],
            'overall_blast': overall['blast'],
            'overall': overall['total']
        })

    return results
