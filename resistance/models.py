"""
Resistance Application Models.

These are models to store information on the predicted resistance phenotypes of
Staphopia samples.
"""
from django.db import models

from gene.models import Clusters
from variant.models import SNP


class Name(models.Model):
    name = models.TextField()


class Publication(models.Model):
    pmid = models.TextField()


class Phenotype(models.Model):
    name = models.ForeignKey('Name', on_delete=models.CASCADE)
    publication = models.ForeignKey('Publication', on_delete=models.CASCADE)
    predicted_mic = models.TextField()


class Genotype(models.Model):
    phenotype = models.ForeignKey('Phenotype', on_delete=models.CASCADE)
    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)


class Variant(models.Model):
    gene = models.ForeignKey('Gene', on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    substitution = models.TextField()


class ToSNP(models.Model):
    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    snp = models.ForeignKey(SNP, on_delete=models.CASCADE,
                            related_name='resistance_snp')


class Gene(models.Model):
    cluster = models.ForeignKey(Clusters, on_delete=models.CASCADE, default=0)
    name = models.TextField()
    product = models.TextField()
    dna = models.TextField()
    aa = models.TextField()
