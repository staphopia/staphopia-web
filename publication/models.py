from django.db import models

from sample.models import Sample


class ToSample(models.Model):
    """Link publications to samples."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='publication_sample')
    publication = models.ForeignKey('Publication', on_delete=models.CASCADE)


class Publication(models.Model):
    """Pubmed information."""
    pmid = models.PositiveIntegerField(unique=True)
    authors = models.TextField()
    title = models.TextField()
    abstract = models.TextField(db_index=True)
    reference_ids = models.TextField()
    keywords = models.TextField()
