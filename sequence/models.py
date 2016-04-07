"""
Sequence Application Models.

These are models to store information on the sequence quality of Staphopia
samples.
"""
from django.db import models

from sample.models import MetaData


class Stat(models.Model):
    """
    Quality statistics of input FASTQ file.

    Can store original and filtered stats.
    """

    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)
    is_original = models.BooleanField(default=False, db_index=True)
    rank = models.PositiveSmallIntegerField(db_index=True)

    total_bp = models.BigIntegerField()
    coverage = models.DecimalField(max_digits=7, decimal_places=2)

    read_total = models.BigIntegerField(default=0)
    read_min = models.PositiveIntegerField(default=0)
    read_mean = models.DecimalField(default=0.0, max_digits=11,
                                    decimal_places=4)
    read_std = models.DecimalField(default=0.0, max_digits=11,
                                   decimal_places=4)
    read_median = models.PositiveIntegerField(default=0)
    read_max = models.PositiveIntegerField(default=0)
    read_25th = models.PositiveIntegerField(default=0)
    read_75th = models.PositiveIntegerField(default=0)

    qual_mean = models.DecimalField(max_digits=7, decimal_places=4)
    qual_std = models.DecimalField(max_digits=7, decimal_places=4)
    qual_median = models.PositiveIntegerField()
    qual_25th = models.PositiveIntegerField()
    qual_75th = models.PositiveIntegerField()

    class Meta:
        unique_together = ('sample', 'is_original')

    def sample_tag(self):
        """Display sample tag in admin view."""
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'sample'

    def sequence_rank(self):
        """Display medal rank in admin view."""
        ranks = {1: 'Bronze', 2: 'Silver', 3: 'Gold'}
        return ranks[self.rank]
    sequence_rank.short_description = 'Rank'
    sequence_rank.admin_order_field = 'rank'


class Length(models.Model):
    """
    Read length counts of input FASTQ file.

    Can store original and filtered stats.
    """

    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)
    is_original = models.BooleanField(default=False, db_index=True)
    length = models.TextField()
    count = models.BigIntegerField()

    class Meta:
        unique_together = ('sample', 'is_original')


class Quality(models.Model):
    """
    Read length counts of input FASTQ file.

    Can store original and filtered stats.
    """

    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)
    is_original = models.BooleanField(default=False, db_index=True)
    position = models.TextField()
    quality = models.DecimalField(max_digits=7, decimal_places=4)

    class Meta:
        unique_together = ('sample', 'is_original')
