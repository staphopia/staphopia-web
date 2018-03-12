from django.db import models


class History(models.Model):
    """Capture search queries (anonymously) to aid in improving searches."""
    query = models.TextField()
    count = models.PositiveIntegerField()
