from django import template

from sample.models import MetaData
from assembly.models import Stats
from sequence.models import Quality

register = template.Library()


@register.assignment_tag
def get_meta_data(sample_tag):
    sample = MetaData.objects.get(sample_tag=sample_tag)
    return sample


@register.assignment_tag
def get_sequence_quality(sample_tag):
    sample = MetaData.objects.get(sample_tag=sample_tag)
    quality = Quality.objects.filter(sample=sample).order_by('-is_original')
    return quality


@register.assignment_tag
def get_assembly_stats(sample_tag):
    sample = MetaData.objects.get(sample_tag=sample_tag)
    assembly = Stats.objects.get(sample=sample, is_scaffolds=False)
    assembly.gc = assembly.contig_percent_g + assembly.contig_percent_c
    return assembly
