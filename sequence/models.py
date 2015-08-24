"""
Sequence Application Models.

These are models to store information on the sequence quality of Staphopia
samples.
"""
from django.db import models

from analysis.models import PipelineVersion
from samples.models import Sample


class Stats(models.Model):

    """
    Statistics of input FASTQ file.

    Can store original and filtered stats.
    """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    is_original = models.BooleanField(default=False, db_index=True)
    version = models.ForeignKey(PipelineVersion, on_delete=models.CASCADE)

    rank = models.PositiveSmallIntegerField(db_index=True)

    total_bp = models.BigIntegerField()
    total_reads = models.BigIntegerField()
    coverage = models.DecimalField(max_digits=7, decimal_places=2)

    min_read_length = models.PositiveIntegerField()
    mean_read_length = models.DecimalField(max_digits=10, decimal_places=3)
    max_read_length = models.PositiveIntegerField()

    qual_mean = models.DecimalField(max_digits=6, decimal_places=3)
    qual_std = models.DecimalField(max_digits=6, decimal_places=3)
    qual_25th = models.DecimalField(max_digits=6, decimal_places=3)
    qual_median = models.DecimalField(max_digits=6, decimal_places=3)
    qual_75th = models.DecimalField(max_digits=6, decimal_places=3)

    class Meta:
        unique_together = ('sample', 'is_original', 'version')

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'sample'

    def sequence_rank(self):
        """ Display medal rank in admin view. """
        ranks = {1: 'Bronze', 2: 'Silver', 3: 'Gold'}
        return ranks[self.rank]
    sequence_rank.short_description = 'Rank'
    sequence_rank.admin_order_field = 'rank'

    def pipeline_version(self):
        """ Display pipeline version in admin view. """
        return self.version.version
    pipeline_version.short_description = 'Pipeline Version'
    pipeline_version.admin_order_field = 'version'
