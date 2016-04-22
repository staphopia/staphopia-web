"""
Gene Application Models.

These are models to store information on the predicted gene annotation of
Staphopia samples.
"""
import architect
from django.db import models

from assembly.models import Contigs
from sample.models import MetaData, Program
from variant.models import Reference


class Clusters(models.Model):
    """UniRef50 Cluster Ids."""

    name = models.TextField(unique=True)
    aa = models.TextField()


class ClusterMembers(models.Model):
    """Each member of a given UniRef50 Cluster."""

    cluster = models.ForeignKey('Clusters', on_delete=models.CASCADE)
    member = models.TextField(unique=True)
    entry_name = models.TextField()
    gene = models.ForeignKey('Names', related_name="gene",
                             on_delete=models.CASCADE)
    protein = models.ForeignKey('Names', related_name="product",
                                on_delete=models.CASCADE)
    organism = models.ForeignKey('Organism', on_delete=models.CASCADE)
    length = models.PositiveIntegerField()
    is_rep = models.BooleanField()
    is_seed = models.BooleanField()


class Names(models.Model):
    """Gene names, and protein products."""

    name = models.TextField()


class Organism(models.Model):
    """The organism of origin for a given protein."""

    taxon_id = models.PositiveIntegerField()
    name = models.TextField()


class References(models.Model):
    """Annotation mapping to Variant references."""

    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    contig = models.ForeignKey(
        'ReferenceSequence', on_delete=models.CASCADE, default=0
    )
    cluster = models.ForeignKey('Clusters', on_delete=models.CASCADE)

    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    is_positive = models.BooleanField()
    is_tRNA = models.BooleanField()
    phase = models.PositiveSmallIntegerField()

    dna = models.TextField()
    aa = models.TextField()

    class Meta:
        unique_together = ('reference', 'contig', 'cluster', 'start', 'end')


class ReferenceSequence(models.Model):
    """Sequence for each reference renamed by PROKKA."""

    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    name = models.TextField(db_index=True)
    sequence = models.TextField()

    class Meta:
        unique_together = ('reference', 'name')


# Create partition every 10 million records
@architect.install('partition', type='range', subtype='integer',
                   constraint='10000000', column='id')
class Features(models.Model):
    """Annotated info for each predicted gene."""

    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)
    contig = models.ForeignKey(Contigs, on_delete=models.CASCADE, default=0)
    cluster = models.ForeignKey('Clusters', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    inference = models.ForeignKey('Inference', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    is_positive = models.BooleanField()
    is_tRNA = models.BooleanField()
    is_rRNA = models.BooleanField()
    phase = models.PositiveSmallIntegerField()

    prokka_id = models.TextField()
    dna = models.TextField()
    aa = models.TextField()

    class Meta:
        unique_together = ('sample', 'contig', 'cluster', 'start', 'end')


class Product(models.Model):
    """Product information for a given annotation."""

    product = models.TextField(db_index=True)


class Inference(models.Model):
    """How the annotation was infered."""

    inference = models.TextField(db_index=True)


class Note(models.Model):
    """Any notes associated with a given annotation."""

    note = models.TextField(db_index=True)


class BlastResults(models.Model):
    """Predicted gene BLAST hits against UniRef50."""

    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)
    feature = models.ForeignKey('Features', on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    bitscore = models.PositiveSmallIntegerField()
    evalue = models.DecimalField(max_digits=7, decimal_places=2)
    identity = models.PositiveSmallIntegerField()
    mismatch = models.PositiveSmallIntegerField()
    gaps = models.PositiveSmallIntegerField()
    hamming_distance = models.PositiveSmallIntegerField()
    query_from = models.PositiveSmallIntegerField()
    query_to = models.PositiveSmallIntegerField()
    query_len = models.PositiveSmallIntegerField()
    hit_from = models.PositiveIntegerField()
    hit_to = models.PositiveIntegerField()
    align_len = models.PositiveSmallIntegerField()

    qseq = models.TextField()
    hseq = models.TextField()
    midline = models.TextField()

    class Meta:
        unique_together = ('sample', 'feature')
