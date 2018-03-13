from django.db import models
from django.contrib.auth.models import User

from sample.models import Sample


class ToSample(models.Model):
    """Link tags to samples."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='tag_sample')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)


class Tag(models.Model):
    """User based tags to associate with a sample."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.TextField(db_index=True)
    comment = models.TextField(blank=True)
    is_public = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('user', 'tag')
