from django import template
from django.db import connection

register = template.Library()


@register.inclusion_tag('top10/contributors.html')
def top10_sequencing_centers():
    cursor = connection.cursor()
    q = "SELECT sequencing_center, count FROM top_sequencing_centers(10)"
    cursor.execute(q)

    return {
        'top_list': cursor.fetchall()
    }


@register.inclusion_tag('top10/sequence_types.html')
def top10_sequence_types():
    cursor = connection.cursor()
    q = "SELECT sequence_type, count FROM top_sequence_types(10)"
    cursor.execute(q)

    return {
        'top_list': cursor.fetchall()
    }
