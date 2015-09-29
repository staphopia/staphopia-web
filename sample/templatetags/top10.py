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
