"""
MLST Application Models.

These are models to store information on the MLST calls for Staphopia samples.
"""
from django.db import models

from sample.models import MetaData


class SequenceTypes(models.Model):

    """ Sequence type mappings from MLST database. """

    st = models.PositiveIntegerField(unique=True)
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

    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)
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
        unique_together = ('sample', 'locus_name', 'locus_id')

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'mlst'


class Srst2(models.Model):

    """ SRST2 results from mapping of FASTQ files. """

    sample = models.OneToOneField(MetaData, on_delete=models.CASCADE)
    st_original = models.TextField()
    st_stripped = models.PositiveIntegerField(default=0, db_index=True)
    is_exact = models.BooleanField(default=False, db_index=True)
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
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'mlst'
