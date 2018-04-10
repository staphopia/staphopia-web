"""API utilities shared across viewsets."""
import time
from collections import OrderedDict

from django.conf import settings
from django.db import connection


def timeit(fun, *args, **kw):
    start_time = time.time()
    results = fun(*args, **kw)
    return [results, (time.time() - start_time) * 1000]


def format_results(results, query_time=None, limit=None):
    """Format query results to be similar to Django Rest Framework output."""
    message = "success"
    if limit:
        message = 'Limited results to {0} of {1}.'.format(
            limit, len(results)
        )
        results = results[0:limit]

    if query_time:
        return OrderedDict((
            ("message", message),
            ("took", f'{float(query_time):.2f} ms'),
            ("count", len(results)),
            ("results", results)
        ))
    else:
        return OrderedDict((
            ("message", message),
            ("count", len(results)),
            ("results", results)
        ))


def get_sample_permisions(sql, ambiguous=False):
    """Determine which samples to show."""
    if settings.VIEW_ALL_SAMPLES:
        # On Dev site, all samples viewable
        sql = sql.replace('USER_PERMISSION', '')
    else:
        # Only ENA data available
        if ambiguous:
            sql = sql.replace('USER_PERMISSION', 'AND s.user_id=2')
        else:
            sql = sql.replace('USER_PERMISSION', 'AND user_id=2')
    return sql


def query_database(sql, ambiguous=False):
    """Submit SQL query to the database."""
    cursor = connection.cursor()
    cursor.execute(get_sample_permisions(sql, ambiguous=ambiguous))
    cols = [d[0] for d in cursor.description]
    return [OrderedDict(zip(cols, row)) for row in cursor.fetchall()]


def sanitized_query(sql, values):
    """Submit SQL query to the database."""
    cursor = connection.cursor()
    cursor.execute(get_sample_permisions(sql), values)
    cols = [d[0] for d in cursor.description]
    return [OrderedDict(zip(cols, row)) for row in cursor.fetchall()]


def get_ids_in_bulk(table, ids, id_col="id"):
    """Return information from a given table for a list of ids."""
    sql = "SELECT * FROM {0} WHERE {1} IN ({2});".format(
        table,
        id_col,
        ','.join([str(i) for i in ids])
    )
    return query_database(sql)
