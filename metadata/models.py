from django.db import models
from django.contrib.auth.models import User

from sample.models import Sample


class Field(models.Model):
    name = models.TextField(unique=True)
    comment = models.TextField()


class History(models.Model):
    """Capture user changes to metadata fields."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    field = models.ForeignKey('Field', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    previous = models.TextField()
    current = models.TextField()


class ToSample(models.Model):
    """Metadata associated with a Sample."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='metadata_sample')
    field = models.ForeignKey('Field', on_delete=models.CASCADE)
    value = models.TextField()
