"""
Gene Application Models.

These are models to store information on the predicted gene annotation of
Staphopia samples.
"""
from django.db import models

from analysis.models import PipelineVersion
from assembly.models import Contigs
from samples.models import Sample
from variant.models import Reference, Annotation


class Clusters(models.Model):

    """ UniRef90 Cluster Ids. """

    cluster = models.TextField(unique=True)
    dna = models.TextField()
    aa = models.TextField()


class ClusterMembers(models.Model):

    """ Each member of a given UniRef90 Cluster. """

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

    """ Gene names, and protein products. """

    name = models.TextField()


class Organism(models.Model):

    """ The organism of origin for a given protein. """

    taxon_id = models.PositiveIntegerField()
    name = models.TextField()


class References(models.Model):

    """ Annotation mapping to Variant references. """

    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    annotation = models.ForeignKey(Annotation)
    cluster = models.ForeignKey('Clusters', on_delete=models.CASCADE)
    dna = models.TextField()
    aa = models.TextField()


class Annotation(models.Model):

    """ Annotated info for each predicted gene. """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey(PipelineVersion, on_delete=models.CASCADE)
    contig = models.ForeignKey(Contigs, on_delete=models.CASCADE)
    cluster = models.ForeignKey('Clusters', on_delete=models.CASCADE)

    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    is_positive = models.BooleanField()
    phase = models.PositiveSmallIntegerField()

    dna = models.TextField()
    aa = models.TextField()

    class Meta:
        unique_together = ('sample', 'version', 'cluster')
