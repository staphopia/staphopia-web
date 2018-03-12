"""
Resistance Application Models.

These are models to store information on the predicted resistance phenotypes of
Staphopia samples with the use of Ariba.
"""
from django.db import models
from django.contrib.postgres.fields import JSONField

from sample.models import Sample
from version.models import Version


class Cluster(models.Model):
    name = models.TextField(unique=True)
    resistance_class = models.TextField(db_index=True)
    mechanism = models.TextField()
    ref_name = models.TextField()
    database = models.TextField()
    headers = models.TextField()


class ResistanceClass(models.Model):
    name = models.TextField(unique=True)


class Ariba(models.Model):
    """Ariba resistance related results."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='resistance_ariba_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='resistance_ariba_version')
    results = JSONField()

    class Meta:
        unique_together = ('sample', 'version')


class AribaSequence(models.Model):
    """Ariba resistance related sequences."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='resistance_aribaseq_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='resistance_aribaseq_version')
    sequences = JSONField()

    class Meta:
        unique_together = ('sample', 'version')
