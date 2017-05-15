"""
Kmer Application Models.

These are models to store information on the Kmer analysis of Staphopia
samples.
"""
from django.db import models

from sample.models import Sample


class FixedCharField(models.Field):
    """Force creation of a CHAR field not VARCHAR."""

    def __init__(self, max_length, *args, **kwargs):
        """Initialize."""
        self.max_length = max_length
        super(FixedCharField, self).__init__(
            max_length=max_length, *args, **kwargs
        )

    def db_type(self, connection):
        """Explicit char."""
        return 'char(%s)' % self.max_length


class Total(models.Model):
    """Total kmer counts from each sample."""

    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()
    singletons = models.PositiveIntegerField()
