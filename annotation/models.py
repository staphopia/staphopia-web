"""
Gene Application Models.

These are models to store information on the predicted gene annotation of
Staphopia samples.
"""
from django.db import models
from django.contrib.postgres.fields import JSONField

from sample.models import Sample
from version.models import Version
from variant.models import Reference, Annotation


class Annotation(models.Model):
    """Annotated info for each predicted gene."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='annotation_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='annotation_version')
    info = JSONField()
    gene = JSONField()
    protein = JSONField()
    rna = JSONField()
    blast = JSONField()

    class Meta:
        unique_together = ('sample', 'version')


class Repeat(models.Model):
    """Annotated repeat regions (CRISPRs) for each predicted gene."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='annotation_repeat_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='annotation_repeat_version')
    repeat = JSONField()

    class Meta:
        unique_together = ('sample', 'version')


class Inference(models.Model):
    """Annotation inferences."""
    inference = models.TextField(db_index=True)
    product = models.TextField(db_index=True)
    note = models.TextField(db_index=True)
    name = models.TextField()

    class Meta:
        unique_together = ('inference', 'product', 'note', 'name')


class Feature(models.Model):
    """Annotation feature types."""
    feature = models.TextField(unique=True)
