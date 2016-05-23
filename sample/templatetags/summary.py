from django import template

from ena.models import CenterNames, Experiment
from sample.models import MetaData
from assembly.models import Stats
from mlst.models import Srst2

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_meta_data(context, sample_tag):
    sample = MetaData.objects.get(sample_tag=sample_tag)
    return sample


@register.assignment_tag(takes_context=True)
def get_mlst_data(context, sample):
    mlst = Srst2.objects.get(sample=sample)
    return mlst


@register.assignment_tag
def get_taxon_id(sample_tag):
    exp = Experiment.objects.get(experiment_accession=sample_tag)
    return exp.tax_id


@register.simple_tag
def get_center_name(center_name):
    try:
        center = CenterNames.objects.get(ena_name=center_name)
        return center.name
    except CenterNames.DoesNotExist:
        return '-'


@register.assignment_tag
def get_sequence_quality(sample_tag):
    sample = MetaData.objects.get(sample_tag=sample_tag)
    # quality = Quality.objects.filter(sample=sample).order_by('-is_original')
    return 0


@register.assignment_tag
def get_assembly_stats(sample_tag):
    sample = MetaData.objects.get(sample_tag=sample_tag)
    assembly = Stats.objects.get(sample=sample, is_scaffolds=False)
    assembly.gc = assembly.contig_percent_g + assembly.contig_percent_c
    return assembly
