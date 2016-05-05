"""
SCCmec Application Models.

These are models to store information on the SCCmec related results.
"""
from django.db import models

from sample.models import Sample
from staphopia.models import GenericBlast


class Cassette(models.Model):
    """Basic info for each SCCmec cassette."""

    name = models.TextField()
    header = models.TextField()
    length = models.PositiveIntegerField()
    meca_start = models.PositiveIntegerField(default=0)
    meca_stop = models.PositiveIntegerField(default=0)
    meca_length = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('name', 'header')


class Coverage(models.Model):
    """Coverage statistics for each SCCmec cassette."""

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    cassette = models.ForeignKey('Cassette', on_delete=models.CASCADE)

    total = models.DecimalField(max_digits=7, decimal_places=2)

    minimum = models.PositiveIntegerField()
    mean = models.DecimalField(max_digits=7, decimal_places=2)
    median = models.PositiveIntegerField()
    maximum = models.PositiveIntegerField()

    meca_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    meca_minimum = models.PositiveIntegerField(default=0)
    meca_mean = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    meca_median = models.PositiveIntegerField(default=0)
    meca_maximum = models.PositiveIntegerField(default=0)
    per_base_coverage = models.TextField()

    def sample_tag(self):
        """Display sample tag in admin view."""
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'sample'

    class Meta:
        unique_together = ('sample', 'cassette')


class Primers(GenericBlast):
    """BLAST hits against SCCmec primers."""

    pass


class Proteins(GenericBlast):
    """BLAST hits against SCCmec proteins."""

    pass
