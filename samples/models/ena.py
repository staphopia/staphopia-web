from django.db import models

from samples.models.sample import Sample

class EnaToSample(models.Model):
    '''
    
    '''
    experiment_accession = models.ForeignKey('EnaExperiment', 
                                             db_column='experiment_accession',
                                             on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    
    class Meta: 
        unique_together = ('experiment_accession', 'sample')
        app_label = 'samples' 
        
class EnaStudy(models.Model):
    '''
    
    '''
    study_accession = models.TextField(primary_key=True)
    secondary_study_accession = models.TextField() 
    study_title = models.TextField() 
    study_alias = models.TextField() 

    class Meta: 
        app_label = 'samples' 
    
class EnaExperiment(models.Model):
    '''
    
    '''
    experiment_accession = models.TextField(primary_key=True)
    experiment_title = models.TextField() 
    experiment_alias = models.TextField() 
    study_accession = models.ForeignKey('EnaStudy', 
                                        db_column='study_accession',
                                        on_delete=models.CASCADE)
    sample_accession = models.TextField() 
    secondary_sample_accession = models.TextField() 
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
        
class EnaRun(models.Model):
    '''
    
    '''
    run_accession = models.TextField(primary_key=True) 
    experiment_accession = models.ForeignKey('EnaExperiment', 
                                             db_column='experiment_accession',
                                             on_delete=models.CASCADE)
    is_paired = models.BooleanField() 
    run_alias = models.TextField() 
    read_count = models.PositiveIntegerField() 
    base_count = models.PositiveIntegerField() 
    mean_read_length = models.DecimalField(max_digits=10, decimal_places=2)
    coverage = models.DecimalField(max_digits=10, decimal_places=2)
    first_public = models.TextField() 
    fastq_bytes = models.TextField() 
    fastq_md5 = models.TextField() 
    fastq_aspera = models.TextField() 
    fastq_ftp = models.TextField() 

    class Meta: 
        app_label = 'samples' 
     
class EnaQueue(models.Model):
    '''
    
    '''
    experiment_accession = models.ForeignKey('EnaExperiment', 
                                             db_column='experiment_accession',
                                             on_delete=models.CASCADE,
                                             primary_key=True)
    is_waiting = models.BooleanField() 
    
    class Meta: 
        app_label = 'samples' 