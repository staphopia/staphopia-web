"""
MLST Application Models.

These are models to store information on the MLST calls for Staphopia samples.
"""
from django.db import models

from sample.models import Sample
from version.models import Version


class SequenceTypes(models.Model):
    """Sequence type mappings from MLST database."""
    st = models.PositiveIntegerField(unique=True)
    arcc = models.PositiveIntegerField()
    aroe = models.PositiveIntegerField()
    glpf = models.PositiveIntegerField()
    gmk = models.PositiveIntegerField()
    pta = models.PositiveIntegerField()
    tpi = models.PositiveIntegerField()
    yqil = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now=True)


class MLST(models.Model):
    """ST determined from Ariba, Mentalist and BLAST."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='mlst_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='mlst_version')
    st = models.PositiveIntegerField(db_index=True)
    ariba = models.PositiveIntegerField(db_index=True)
    mentalist = models.PositiveIntegerField(db_index=True)
    blast = models.PositiveIntegerField(db_index=True)

    class Meta:
        unique_together = ('sample', 'version')


class Report(models.Model):
    """Output from each program used to determine MLST."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='mlst_report_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='mlst_report_version')
    ariba = models.TextField()
    mentalist = models.TextField()
    blast = models.TextField()

    class Meta:
        unique_together = ('sample', 'version')
