"""
Generic Models.

These are models are generic base models.
"""
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from assembly.models import Contig
from sample.models import Sample
from version.models import Version


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class BlastQuery(models.Model):
    """Store the query title of blast results."""

    title = models.TextField()
    length = models.PositiveIntegerField()

    class Meta:
        unique_together = ('title', 'length')


class GenericBlast(models.Model):
    """Unique 31-mer strings stored as strings."""

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    contig = models.ForeignKey(Contig, on_delete=models.CASCADE)
    query = models.ForeignKey('staphopia.BlastQuery', on_delete=models.CASCADE)

    bitscore = models.PositiveSmallIntegerField()
    evalue = models.DecimalField(max_digits=7, decimal_places=2)
    identity = models.PositiveSmallIntegerField()
    mismatch = models.PositiveSmallIntegerField()
    gaps = models.PositiveSmallIntegerField()
    hamming_distance = models.PositiveSmallIntegerField()
    query_from = models.PositiveSmallIntegerField()
    query_to = models.PositiveSmallIntegerField()
    hit_from = models.PositiveIntegerField()
    hit_to = models.PositiveIntegerField()
    align_len = models.PositiveSmallIntegerField()

    qseq = models.TextField()
    hseq = models.TextField()
    midline = models.TextField()

    class Meta:
        abstract = True
