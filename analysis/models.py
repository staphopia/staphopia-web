from django.db import models

from samples.models import Sample

class PipelineVersions(models.Model):
    '''
    
    '''
    module = models.TextField()
    version = models.TextField()
    
    class Meta: 
        unique_together = ('module', 'version')

class Programs(models.Model):
    '''
    
    '''
    pipeline = models.ForeignKey('PipelineVersions', on_delete=models.CASCADE)
    program = models.TextField()
    version = models.TextField()
    
    class Meta: 
        unique_together = ('pipeline', 'program', 'version')
        
class FastqStats(models.Model):
    '''
    
    '''
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    is_original = models.BooleanField(default=False, db_index=True)
    version = models.ForeignKey('PipelineVersions', on_delete=models.CASCADE)
    
    rank = models.PositiveSmallIntegerField(db_index=True)
    
    total_bp = models.PositiveIntegerField()
    total_reads = models.PositiveIntegerField()
    coverage = models.DecimalField(max_digits=6, decimal_places=3)
    
    min_read_length = models.PositiveIntegerField()
    mean_read_length = models.DecimalField(max_digits=10, decimal_places=3)
    max_read_length = models.PositiveIntegerField()
    
    qual_mean = models.DecimalField(max_digits=6, decimal_places=3)
    qual_std = models.DecimalField(max_digits=6, decimal_places=3)
    qual_25th = models.DecimalField(max_digits=6, decimal_places=3)
    qual_median = models.DecimalField(max_digits=6, decimal_places=3)
    qual_75th = models.DecimalField(max_digits=6, decimal_places=3)
    
    class Meta: 
        unique_together = ('sample', 'is_original', 'version')
    
class AssemblyStats(models.Model):
    '''
    
    '''
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    is_scaffolds = models.BooleanField(default=False, db_index=True)
    version = models.ForeignKey('PipelineVersions', on_delete=models.CASCADE)
    
    total_contig = models.PositiveSmallIntegerField()
    total_contig_length = models.PositiveIntegerField()

    min_contig_length = models.PositiveIntegerField()
    median_contig_length = models.PositiveIntegerField()
    mean_contig_length = models.DecimalField(max_digits=9, decimal_places=2)
    max_contig_length = models.PositiveIntegerField()

    n50_contig_length = models.PositiveIntegerField()
    l50_contig_count = models.PositiveSmallIntegerField()
    ng50_contig_length = models.PositiveIntegerField()
    lg50_contig_count = models.PositiveSmallIntegerField()

    contigs_greater_1k = models.PositiveSmallIntegerField()
    contigs_greater_10k = models.PositiveSmallIntegerField()
    contigs_greater_100k = models.PositiveSmallIntegerField()
    contigs_greater_1m = models.PositiveSmallIntegerField()

    percent_contigs_greater_1k = models.DecimalField(max_digits=4, 
                                                     decimal_places=2)
    percent_contigs_greater_10k = models.DecimalField(max_digits=4, 
                                                      decimal_places=2)
    percent_contigs_greater_100k = models.DecimalField(max_digits=4, 
                                                       decimal_places=2)
    percent_contigs_greater_1m = models.DecimalField(max_digits=4, 
                                                     decimal_places=2)

    contig_percent_a = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_t = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_g = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_c = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_n = models.DecimalField(max_digits=4, decimal_places=2)
    contig_non_acgtn = models.DecimalField(max_digits=4, decimal_places=2)
    num_contig_non_acgtn = models.PositiveSmallIntegerField()
    
    class Meta: 
        unique_together = ('sample', 'is_scaffolds', 'version')        

class Kmer(models.Model):
    '''
    
    '''
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey('PipelineVersions', on_delete=models.CASCADE)
    
    class Meta: 
        unique_together = ('sample', 'version')   
        
class KmerString(models.Model):
    '''
    
    '''
    kmer = models.CharField(default='', max_length=31, unique=True)
    
class KmerCount(models.Model):
    '''
    
    '''
    kmer = models.ForeignKey('Kmer', on_delete=models.CASCADE)
    string = models.ForeignKey('KmerString', on_delete=models.CASCADE)
    count = models.PositiveIntegerField()
    
    class Meta: 
        unique_together = ('kmer', 'string') 
    
class KmerTotal(models.Model):
    '''
    
    '''
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()
    
  