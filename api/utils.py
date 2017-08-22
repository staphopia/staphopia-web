"""API utilities shared across viewsets."""
from collections import OrderedDict

from django.db import connection


def format_results(results, time=None, limit=None):
    """Format query results to be similar to Django Rest Framework output."""
    message = "success"
    if limit:
        message = 'Limited results to {0} of {1}.'.format(
            limit, len(results)
        )
        results = results[0:limit]

    if time:
        return OrderedDict((
            ("took", time),

            ("count", len(results)),
            ("results", results)
        ))
    else:
        return OrderedDict((
            ("message", message),
            ("count", len(results)),
            ("results", results)
        ))


def query_database(sql):
    """Submit SQL query to the database."""
    cursor = connection.cursor()
    cursor.execute(sql)
    cols = [d[0] for d in cursor.description]
    return [OrderedDict(zip(cols, row)) for row in cursor.fetchall()]


def sanitized_query(sql, values):
    """Submit SQL query to the database."""
    cursor = connection.cursor()
    cursor.execute(sql, values)
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
