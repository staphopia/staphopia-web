"""Models associated with Sample."""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


class Sample(models.Model):
    """Basic sample information."""

    user = models.ForeignKey(User, models.CASCADE)
    name = models.TextField(db_index=True, default='')
    is_public = models.BooleanField(default=True, db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)
    is_flagged = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('user', 'name')


class Flag(models.Model):
    """Reason for flagging a sample."""

    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    reason = models.TextField()

    class Meta:
        unique_together = ('sample', 'reason')


class MD5(models.Model):
    """
    Store the original input MD5sum to make sure we have not already stored
    the sample already.
    """
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    md5sum = models.CharField(max_length=32, unique=True)


class Metadata(models.Model):
    """
    Store metadata associated with each sample.
    """
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    metadata = JSONField()
    history = JSONField()


class MetadataFields(models.Model):
    """Metadata related fields and descriptions."""
    field = models.TextField(unique=True)
    description = models.TextField(db_index=True, default='')
