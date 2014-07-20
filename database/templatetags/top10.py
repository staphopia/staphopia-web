from django import template
from database.models import Summary
from collections import Counter
register = template.Library()

@register.inclusion_tag('base_top10.html')
def top10_table(title, col_title, col_name):
    return {'title':title,'col_title':col_title,
            'top_list': Counter(Summary.objects.values_list(col_name,
                                                            flat=True)).most_common(10)}
