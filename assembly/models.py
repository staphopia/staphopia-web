"""
Assembly Application Models.

These are models to store information on the assembly quality of Staphopia
samples.
"""
from django.db import models

from sample.models import MetaData


class Stats(models.Model):

    """
    Statistics of the assembled genome.

    Both contigs and scaffolds are stored.
    """

    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)
    is_scaffolds = models.BooleanField(default=False, db_index=True)

    total_contig = models.PositiveSmallIntegerField()
    total_contig_length = models.PositiveIntegerField()

    min_contig_length = models.PositiveIntegerField()
    median_contig_length = models.PositiveIntegerField()
    mean_contig_length = models.DecimalField(max_digits=9, decimal_places=2)
    max_contig_length = models.PositiveIntegerField()

    n50_contig_length = models.PositiveIntegerField(default=0)
    l50_contig_count = models.PositiveSmallIntegerField(default=0)
    ng50_contig_length = models.PositiveIntegerField(default=0)
    lg50_contig_count = models.PositiveSmallIntegerField(default=0)

    contigs_greater_1k = models.PositiveSmallIntegerField()
    contigs_greater_10k = models.PositiveSmallIntegerField()
    contigs_greater_100k = models.PositiveSmallIntegerField()
    contigs_greater_1m = models.PositiveSmallIntegerField()

    percent_contigs_greater_1k = models.DecimalField(max_digits=4,
                                                     decimal_places=2)
    percent_contigs_greater_10k = models.DecimalField(max_digits=4,
                                                      decimal_places=2)
    percent_contigs_greater_100k = models.DecimalField(max_digits=4,
                                                       decimal_places=2)
    percent_contigs_greater_1m = models.DecimalField(max_digits=4,
                                                     decimal_places=2)

    contig_percent_a = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_t = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_g = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_c = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_n = models.DecimalField(max_digits=4, decimal_places=2)
    contig_non_acgtn = models.DecimalField(max_digits=4, decimal_places=2)
    num_contig_non_acgtn = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('sample', 'is_scaffolds')

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'sample'
