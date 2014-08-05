from django.db import models
from django.contrib.auth.models import User

class Sample(models.Model):
    # New Sample
    sample_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sample_tag = models.TextField(db_index=True, blank=True, default='')

    # Project Information
    contact_name = models.TextField(default='')
    contact_email = models.EmailField(default='')
    contact_link = models.URLField(default='', blank=True)
    sequencing_center = models.TextField(default='')
    sequencing_center_link = models.URLField(default='', blank=True)
    sequencing_date = models.DateField(default='1900-01-01', blank=True)
    sequencing_libaray_method = models.TextField(default='', blank=True)
    sequencing_platform = models.TextField(default='', blank=True)

    # Publication Inforamtion
    publication_link = models.URLField(default='', blank=True)
    pubmed_id = models.TextField(default='', blank=True)
    doi = models.TextField(default='', blank=True)
    funding_agency = models.TextField(default='', blank=True)
    funding_agency_link = models.URLField(default='', blank=True)

    # Organism Information
    strain = models.TextField(default='', blank=True)
    isolation_date = models.DateField(default='1900-01-01', blank=True)
    isolation_country = models.TextField(default='', blank=True)
    isolation_city = models.TextField(default='', blank=True)
    isolation_region = models.TextField(default='', blank=True)
    host_name = models.TextField(default='', blank=True)
    host_health = models.TextField(default='', blank=True)
    host_age = models.PositiveSmallIntegerField(default=0, blank=True)
    host_gender = models.TextField(default='', blank=True)
    comments = models.TextField(default='', blank=True)
                         
    # Phenotype Information
    vancomycin_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                         blank=True, default=-200.00)
    penicillin_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                         blank=True, default=-200.00)
    oxacillin_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                        blank=True, default=-200.00)
    clindamycin_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                          blank=True, default=-200.00)
    daptomycin_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                         blank=True, default=-200.00)
    levofloxacin_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                           blank=True, default=-200.00)
    linezolid_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                        blank=True, default=-200.00)
    rifampin_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                       blank=True, default=-200.00)
    tetracycline_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                           blank=True, default=-200.00)
    trimethoprim_mic = models.DecimalField(max_digits=6, decimal_places=3, 
                                           blank=True, default=-200.00)
    source = models.TextField(default='', blank=True)

    # Sequence Information
    is_public = models.BooleanField(default=True, db_index=True)
    is_paired = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False, db_index=True)
    
def content_file_name(instance, filename):
    new_name = '{0}_{1}_original.{2}'.format(
        instance.sample.user.username, 
        str(instance.sample.sample_id).zfill(6),
        filename.split('.', 1)[1]
    )
    return '/'.join(['uploads', instance.sample.user.username, 
                     str(instance.sample.sample_id).zfill(6), new_name])
    
class Upload(models.Model):
    sample = models.OneToOneField('Sample', primary_key=True, on_delete=models.CASCADE)
    path = models.FileField(default='', upload_to=content_file_name)
    md5sum = models.CharField(default='', max_length=32, unique=True)
