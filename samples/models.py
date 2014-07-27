from django.db import models
from django.contrib.auth.models import User

class Sample(models.Model):
    sample_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    is_public = models.BooleanField()
    
class Upload(models.Model):
    sample_id = models.ForeignKey('Sample')
    upload = models.FileField(upload_to='.')
    upload_md5sum = models.CharField(max_length=32)
    analysis_status = models.PositiveSmallIntegerField(max_length=3)
    
class MetaData(models.Model):
    sample_id = models.ForeignKey('Sample')
    field = models.CharField(max_length=50)
    value = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('sample_id', 'field')