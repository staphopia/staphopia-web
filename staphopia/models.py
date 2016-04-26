"""
Generic Models.

These are models are generic base models.
"""
from django.db import models

from assembly.models import Contigs
from sample.models import Sample, Program


class BlastQuery(models.Model):
    """Store the query title of blast results."""

    title = models.TextField()
    length = models.PositiveIntegerField()

    class Meta:
        unique_together = ('title', 'length')


class GenericBlast(models.Model):
    """Unique 31-mer strings stored as strings."""

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    contig = models.ForeignKey(Contigs, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    query = models.ForeignKey('staphopia.BlastQuery', on_delete=models.CASCADE)

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
        abstract = True
