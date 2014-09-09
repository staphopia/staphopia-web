from django.db import models

from samples.models.sample import Sample

class EnaToSample(models.Model):
    '''
    
    '''
    ena = models.ForeignKey('EnaInfo', on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    
    class Meta: 
        unique_together = ('ena', 'sample')
        app_label = 'samples' 
        
class EnaInfo(models.Model):
    '''
    
    '''
    experiment_accession = models.TextField(primary_key=True)
    study_accession = models.TextField() 
    sample_accession = models.TextField() 
    submission_accession = models.TextField() 
    tax_id = models.TextField() 
    scientific_name = models.TextField() 
    instrument_platform = models.TextField(db_index=True, default='') 
    instrument_model = models.TextField() 
    library_layout = models.TextField()  
    library_strategy = models.TextField()  
    library_selection = models.TextField() 
    center_name = models.TextField()  

    class Meta: 
        app_label = 'samples' 
        
class EnaRuns(models.Model):
    '''
    
    '''
    ena = models.ForeignKey('EnaInfo', on_delete=models.CASCADE)
    is_paired = models.BooleanField(default=False)
    run_accession = models.TextField() 
    read_count = models.PositiveIntegerField() 
    base_count = models.PositiveIntegerField() 
    mean_read_length = models.DecimalField(max_digits=9, decimal_places=2)
    coverage = models.DecimalField(max_digits=6, decimal_places=2)
    first_public = models.TextField() 
    fastq_bytes = models.TextField() 
    fastq_md5 = models.TextField() 
    fastq_aspera = models.TextField() 
    fastq_ftp = models.TextField() 
    
    class Meta: 
        app_label = 'samples' 
        