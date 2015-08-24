"""
MLST Application Models.

These are models to store information on the MLST calls for Staphopia samples.
"""
from django.db import models

from analysis.models import PipelineVersion
from samples.models import Sample


class MLST(models.Model):

    """ MLST results from the analysis pipeline. """

    sample = models.ForeignKey(Sample, related_name="mlst_sample_id",
                               on_delete=models.CASCADE)
    version = models.ForeignKey(PipelineVersion,
                                related_name="mlst_version_id",
                                on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sample', 'version')

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'mlst'

    def pipeline_version(self):
        """ Display pipeline version in admin view. """
        return self.version.version
    pipeline_version.short_description = 'Pipeline Version'
    pipeline_version.admin_order_field = 'version'


class SequenceTypes(models.Model):

    """ Sequence type mappings from MLST database. """

    ST = models.PositiveIntegerField(unique=True)
    arcc = models.PositiveIntegerField()
    aroe = models.PositiveIntegerField()
    glpf = models.PositiveIntegerField()
    gmk = models.PositiveIntegerField()
    pta = models.PositiveIntegerField()
    tpi = models.PositiveIntegerField()
    yqil = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now=True)


class Blast(models.Model):

    """ Blast results from contigs against MLST loci. """

    mlst = models.ForeignKey('MLST', on_delete=models.CASCADE)
    locus_name = models.CharField(max_length=4)
    locus_id = models.PositiveSmallIntegerField()
    bitscore = models.PositiveSmallIntegerField()
    slen = models.PositiveSmallIntegerField()
    length = models.PositiveSmallIntegerField()
    gaps = models.PositiveSmallIntegerField()
    mismatch = models.PositiveSmallIntegerField()
    pident = models.DecimalField(max_digits=5, decimal_places=2)
    evalue = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        unique_together = ('mlst', 'locus_name', 'locus_id')

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.mlst.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'mlst'


class Srst2(models.Model):

    """ SRST2 results from mapping of FASTQ files. """

    mlst = models.ForeignKey('MLST', on_delete=models.CASCADE)
    ST = models.TextField()
    arcc = models.TextField()
    aroe = models.TextField()
    glpf = models.TextField()
    gmk = models.TextField()
    pta = models.TextField()
    tpi = models.TextField()
    yqil = models.TextField()
    mismatches = models.TextField()
    uncertainty = models.TextField()
    depth = models.DecimalField(max_digits=8, decimal_places=3)
    maxMAF = models.DecimalField(max_digits=11, decimal_places=7)

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.mlst.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'mlst'
