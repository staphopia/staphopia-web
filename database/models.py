# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals
from django.db import models

def get_sequencing_grade(meanlength, coverage, quality):
    if meanlength >= 75:
        if coverage >= 45 and quality >= 30:
            return 'Gold'
        elif coverage >= 20 and quality >= 20:
            return 'Silver'
        else:
            return 'Bronze'
    else:
        return 'Bronze'

class Summary(models.Model):
    from collections import Counter
    sampleid = models.IntegerField(db_column='SampleID', primary_key=True) # Field name made lowercase.
    sampletag = models.CharField(db_column='SampleTag', max_length=13) # Field name made lowercase.
    username = models.CharField(db_column='UserName', max_length=15) # Field name made lowercase.
    userid = models.IntegerField(db_column='UserID') # Field name made lowercase.
    basecount = models.IntegerField(db_column='BaseCount') # Field name made lowercase.
    readcount = models.IntegerField(db_column='ReadCount') # Field name made lowercase.
    minlength = models.IntegerField(db_column='MinLength') # Field name made lowercase.
    meanlength = models.IntegerField(db_column='MeanLength') # Field name made lowercase.
    maxlength = models.IntegerField(db_column='MaxLength') # Field name made lowercase.
    quality = models.DecimalField(db_column='Quality', max_digits=5, decimal_places=3) # Field name made lowercase.
    coverage = models.DecimalField(db_column='Coverage', max_digits=7, decimal_places=3) # Field name made lowercase.
    n50 = models.IntegerField(db_column='N50') # Field name made lowercase.
    gc = models.DecimalField(db_column='GC', max_digits=4, decimal_places=2) # Field name made lowercase.
    totalcontigs = models.IntegerField(db_column='TotalContigs') # Field name made lowercase.
    totalsize = models.IntegerField(db_column='TotalSize') # Field name made lowercase.
    mean = models.IntegerField(db_column='Mean') # Field name made lowercase.
    median = models.IntegerField(db_column='Median') # Field name made lowercase.
    maxcontig = models.IntegerField(db_column='MaxContig') # Field name made lowercase.
    mincontig = models.IntegerField(db_column='MinContig') # Field name made lowercase.
    greater500 = models.IntegerField(db_column='Greater500') # Field name made lowercase.
    greater1k = models.IntegerField(db_column='Greater1K') # Field name made lowercase.
    greater10k = models.IntegerField(db_column='Greater10K') # Field name made lowercase.
    greater100k = models.IntegerField(db_column='Greater100K') # Field name made lowercase.
    sequencetype = models.IntegerField(db_column='SequenceType') # Field name made lowercase.
    clonalcomplex = models.IntegerField(db_column='ClonalComplex') # Field name made lowercase.
    coveragetype = models.IntegerField(db_column='CoverageType') # Field name made lowercase.
    primertype = models.IntegerField(db_column='PrimerType') # Field name made lowercase.
    proteintype = models.IntegerField(db_column='ProteinType') # Field name made lowercase.
    submitdate = models.DateTimeField(db_column='SubmitDate') # Field name made lowercase.
    resistancehits = models.IntegerField(db_column='ResistanceHits') # Field name made lowercase.
    virulencehits = models.IntegerField(db_column='VirulenceHits') # Field name made lowercase.
    assemblyversion = models.DecimalField(db_column='AssemblyVersion', max_digits=5, decimal_places=3) # Field name made lowercase.
    filterversion = models.DecimalField(db_column='FilterVersion', max_digits=5, decimal_places=3) # Field name made lowercase.
    sequencetypeversion = models.DecimalField(db_column='SequenceTypeVersion', max_digits=5, decimal_places=3) # Field name made lowercase.
    sccmecversion = models.DecimalField(db_column='SCCmecVersion', max_digits=5, decimal_places=3) # Field name made lowercase.
    resistanceversion = models.DecimalField(db_column='ResistanceVersion', max_digits=5, decimal_places=3) # Field name made lowercase.
    virulenceversion = models.DecimalField(db_column='VirulenceVersion', max_digits=5, decimal_places=3) # Field name made lowercase.
    ispublic = models.TextField(db_column='IsPublic') # Field name made lowercase. This field type is a guess.
    ispublished = models.TextField(db_column='IsPublished') # Field name made lowercase. This field type is a guess.
    metadata = models.TextField(db_column='MetaData') # Field name made lowercase.
    sequencingcenter = models.CharField(db_column='SequencingCenter', max_length=120) # Field name made lowercase.
    strain = models.CharField(db_column='Strain', max_length=60) # Field name made lowercase.
    top_seq_centers = Counter(sequencingcenter.choices).most_common(10)
    top_st = Counter(sequencetype.choices).most_common(10)
    top_cc = Counter(clonalcomplex.choices).most_common(10)

    class Meta:
        managed = False
        app_label = 'database'
        db_table = 'Summary'
