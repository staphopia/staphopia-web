"""
CGMLST Application Models.

Models to store information on the CGMLST calls for Staphopia samples.
"""
from django.db import models
from django.contrib.postgres.fields import JSONField

from sample.models import Sample
from version.models import Version


class CGMLST(models.Model):
    """CGMLST determined by Mentalist."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='cgmlst_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='cgmlst_version')
    mentalist = JSONField()

    class Meta:
        unique_together = ('sample', 'version')


class Loci(models.Model):
    """CGMLST loci names to reduce text storage."""
    name = models.TextField(unique=True)


class Report(models.Model):
    """Output from each program used to determine MLST."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='cgmlst_report_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='cgmlst_report_version')
    mentalist = models.TextField()

    class Meta:
        unique_together = ('sample', 'version')
