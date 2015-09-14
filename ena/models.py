from django.db import models

from sample.models import MetaData


class ToSample(models.Model):
    '''

    '''
    experiment_accession = models.ForeignKey('Experiment',
                                             db_column='experiment_accession',
                                             on_delete=models.CASCADE)
    sample = models.ForeignKey(MetaData, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('experiment_accession', 'sample')


class Study(models.Model):
    '''

    '''
    study_accession = models.TextField(primary_key=True)
    secondary_study_accession = models.TextField()
    study_title = models.TextField()
    study_alias = models.TextField()


class Experiment(models.Model):
    '''

    '''
    experiment_accession = models.TextField(primary_key=True)
    experiment_title = models.TextField()
    experiment_alias = models.TextField()
    study_accession = models.ForeignKey('Study',
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


class Run(models.Model):
    '''

    '''
    run_accession = models.TextField(primary_key=True)
    experiment_accession = models.ForeignKey('Experiment',
                                             db_column='experiment_accession',
                                             on_delete=models.CASCADE)
    is_paired = models.BooleanField(default=False)
    run_alias = models.TextField()
    read_count = models.BigIntegerField()
    base_count = models.BigIntegerField()
    mean_read_length = models.DecimalField(max_digits=10, decimal_places=2)
    coverage = models.DecimalField(max_digits=10, decimal_places=2)
    first_public = models.TextField()
    fastq_bytes = models.TextField()
    fastq_md5 = models.TextField()
    fastq_aspera = models.TextField()
    fastq_ftp = models.TextField()


class Publication(models.Model):
    '''

    '''
    experiment_accession = models.ForeignKey('Experiment',
                                             db_column='experiment_accession',
                                             on_delete=models.CASCADE)
    pmid = models.TextField()

    class Meta:
        unique_together = ('experiment_accession', 'pmid')
