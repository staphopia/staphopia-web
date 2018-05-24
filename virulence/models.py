"""
Resistance Application Models.

These are models to store information on the predicted resistance phenotypes of
Staphopia samples with the use of Ariba.
"""
from django.db import models
from django.contrib.postgres.fields import JSONField

from sample.models import Sample
from staphopia.models import BlastQuery
from version.models import Version


class Cluster(models.Model):
    name = models.TextField(unique=True)
    ref_name = models.TextField()
    original_name = models.TextField()


class Ariba(models.Model):
    """Ariba virulence related results."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='virulence_ariba_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='virulence_ariba_version')
    results = JSONField()
    summary = JSONField(default=[])

    class Meta:
        unique_together = ('sample', 'version')


class AribaSequence(models.Model):
    """Ariba virulence related sequences."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='virulence_aribaseq_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='virulence_aribaseq_version')
    sequences = JSONField()

    class Meta:
        unique_together = ('sample', 'version')


class AgrPrimers(models.Model):
    """BLAST hits against SCCmec primers."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='agr_primers_version')
    query = models.ForeignKey(BlastQuery, on_delete=models.CASCADE)
    contig = models.PositiveIntegerField()

    bitscore = models.PositiveSmallIntegerField()
    evalue = models.DecimalField(max_digits=7, decimal_places=2)
    identity = models.PositiveSmallIntegerField()
    mismatch = models.PositiveSmallIntegerField()
    gaps = models.PositiveSmallIntegerField()
    hamming_distance = models.PositiveSmallIntegerField()
    query_from = models.PositiveSmallIntegerField()
    query_to = models.PositiveSmallIntegerField()
    hit_from = models.PositiveIntegerField()
    hit_to = models.PositiveIntegerField()
    align_len = models.PositiveSmallIntegerField()

    qseq = models.TextField()
    hseq = models.TextField()
    midline = models.TextField()

    class Meta:
        unique_together = ('sample', 'version', 'query')
