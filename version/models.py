from django.db import models


class Version(models.Model):
    """Store Docker tag used to process samples."""
    repo = models.TextField()
    tag = models.TextField(unique=True)
    sha256 = models.CharField(max_length=64, unique=True)

    class Meta:
        unique_together = ('repo', 'tag', 'sha256')
