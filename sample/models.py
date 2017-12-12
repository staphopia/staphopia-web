"""Models associated with Sample."""
from django.db import models
from django.contrib.auth.models import User


class Sample(models.Model):
    """Basic sample information."""

    user = models.ForeignKey(User, models.CASCADE)
    name = models.TextField(db_index=True, default='')
    is_public = models.BooleanField(default=True, db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('user', 'name')


class MD5(models.Model):
    """
    Store the original input MD5sum to make sure we have not already stored
    the sample already.
    """
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    md5sum = models.CharField(max_length=32, unique=True)
