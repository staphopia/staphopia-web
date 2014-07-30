from django.db import models
from django.contrib.auth.models import User

class Sample(models.Model):
    sample_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    is_public = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    is_paired = models.BooleanField(default=False)
    analysis_stage = models.PositiveSmallIntegerField(max_length=3, default=0)
    
def content_file_name(instance, filename):
    new_name = '{0}_{1}_original.{2}'.format(
        instance.sample.user.username, 
        str(instance.sample.sample_id).zfill(6),
        filename.split('.', 1)[1]
    )
    return '/'.join(['uploads', instance.sample.user.username, 
                     str(instance.sample.sample_id).zfill(6), new_name])
    
class Upload(models.Model):
    sample = models.OneToOneField('Sample', primary_key=True)
    upload = models.FileField(upload_to=content_file_name)
    upload_md5sum = models.CharField(max_length=32, unique=True)
    
class MetaData(models.Model):
    sample = models.ForeignKey('Sample')
    field = models.CharField(max_length=50)
    value = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('sample', 'field')