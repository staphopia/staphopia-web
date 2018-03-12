"""
Assembly Application Models.

These are models to store information on the assembly quality of Staphopia
samples.
"""
from django.db import models
from django.contrib.postgres.fields import JSONField

from sample.models import Sample
from version.models import Version


class Contig(models.Model):
    """Assembled contigs for each sample renamed by PROKKA."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='assembly_contig_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='assembly_contig_version')
    spades = models.TextField(db_index=True)
    prokka = models.TextField(db_index=True)
    staphopia = models.TextField(db_index=True)

    class Meta:
        unique_together = ('sample', 'version', 'spades')


class Sequence(models.Model):
    """Assembled contigs for each sample renamed by PROKKA."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='assembly_sequence_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='assembly_sequence_version')
    fasta = JSONField()
    graph = JSONField()

    class Meta:
        unique_together = ('sample', 'version')


class Summary(models.Model):
    """Summary statistics of the assembled genome."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='assembly_summary_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='assembly_summary_version')
    total_contig = models.PositiveIntegerField()
    total_contig_length = models.PositiveIntegerField()

    min_contig_length = models.PositiveIntegerField()
    median_contig_length = models.PositiveIntegerField()
    mean_contig_length = models.DecimalField(max_digits=9, decimal_places=2)
    max_contig_length = models.PositiveIntegerField()

    n50_contig_length = models.PositiveIntegerField(default=0)
    l50_contig_count = models.PositiveIntegerField(default=0)
    ng50_contig_length = models.PositiveIntegerField(default=0)
    lg50_contig_count = models.PositiveIntegerField(default=0)

    contigs_greater_1k = models.PositiveIntegerField()
    contigs_greater_10k = models.PositiveIntegerField()
    contigs_greater_100k = models.PositiveIntegerField()
    contigs_greater_1m = models.PositiveIntegerField()

    percent_contigs_greater_1k = models.DecimalField(max_digits=5,
                                                     decimal_places=2)
    percent_contigs_greater_10k = models.DecimalField(max_digits=5,
                                                      decimal_places=2)
    percent_contigs_greater_100k = models.DecimalField(max_digits=5,
                                                       decimal_places=2)
    percent_contigs_greater_1m = models.DecimalField(max_digits=5,
                                                     decimal_places=2)

    contig_percent_a = models.DecimalField(max_digits=5, decimal_places=2)
    contig_percent_t = models.DecimalField(max_digits=5, decimal_places=2)
    contig_percent_g = models.DecimalField(max_digits=5, decimal_places=2)
    contig_percent_c = models.DecimalField(max_digits=5, decimal_places=2)
    contig_percent_n = models.DecimalField(max_digits=5, decimal_places=2)
    contig_non_acgtn = models.DecimalField(max_digits=5, decimal_places=2)
    num_contig_non_acgtn = models.PositiveIntegerField()

    def sample_tag(self):
        """Display sample tag in admin view."""
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'sample'

    class Meta:
        unique_together = ('sample', 'version')
