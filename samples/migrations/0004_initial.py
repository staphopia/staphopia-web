# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sample'
        db.create_table(u'samples_sample', (
            ('sample_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('sample_tag', self.gf('django.db.models.fields.TextField')(default='', db_index=True, blank=True)),
            ('contact_name', self.gf('django.db.models.fields.TextField')(default='')),
            ('contact_email', self.gf('django.db.models.fields.EmailField')(default='', max_length=75)),
            ('contact_link', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
            ('sequencing_center', self.gf('django.db.models.fields.TextField')(default='')),
            ('sequencing_center_link', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
            ('sequencing_date', self.gf('django.db.models.fields.DateField')(default='1900-01-01', blank=True)),
            ('sequencing_libaray_method', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('sequencing_platform', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('publication_link', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
            ('pubmed_id', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('doi', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('funding_agency', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('funding_agency_link', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
            ('strain', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('isolation_date', self.gf('django.db.models.fields.DateField')(default='1900-01-01', blank=True)),
            ('isolation_country', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('isolation_city', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('isolation_region', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('host_name', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('host_health', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('host_age', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, blank=True)),
            ('host_gender', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('vancomycin_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('penicillin_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('oxacillin_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('clindamycin_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('daptomycin_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('levofloxacin_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('linezolid_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('rifampin_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('tetracycline_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('trimethoprim_mic', self.gf('django.db.models.fields.DecimalField')(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
            ('source', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('is_paired', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('samples', ['Sample'])

        # Adding model 'Upload'
        db.create_table(u'samples_upload', (
            ('sample', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['samples.Sample'], unique=True, primary_key=True)),
            ('path', self.gf('django.db.models.fields.files.FileField')(default='', max_length=100)),
            ('md5sum', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=32)),
        ))
        db.send_create_signal('samples', ['Upload'])

        # Adding model 'PipelineVersions'
        db.create_table(u'samples_pipelineversions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.TextField')()),
            ('version', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('samples', ['PipelineVersions'])

        # Adding unique constraint on 'PipelineVersions', fields ['module', 'version']
        db.create_unique(u'samples_pipelineversions', ['module', 'version'])

        # Adding model 'Programs'
        db.create_table(u'samples_programs', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pipeline', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.PipelineVersions'])),
            ('program', self.gf('django.db.models.fields.TextField')()),
            ('version', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('samples', ['Programs'])

        # Adding unique constraint on 'Programs', fields ['pipeline', 'program', 'version']
        db.create_unique(u'samples_programs', ['pipeline_id', 'program', 'version'])

        # Adding model 'FastqStatistics'
        db.create_table(u'samples_fastqstatistics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Sample'])),
            ('is_original', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.PipelineVersions'])),
            ('rank', self.gf('django.db.models.fields.PositiveSmallIntegerField')(db_index=True)),
            ('total_bp', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('total_reads', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('coverage', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=3)),
            ('min_read_length', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('mean_read_length', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=3)),
            ('max_read_length', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('qual_mean', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=3)),
            ('qual_std', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=3)),
            ('qual_25th', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=3)),
            ('qual_median', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=3)),
            ('qual_75th', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=3)),
        ))
        db.send_create_signal('samples', ['FastqStatistics'])

        # Adding unique constraint on 'FastqStatistics', fields ['sample', 'is_original', 'version']
        db.create_unique(u'samples_fastqstatistics', ['sample_id', 'is_original', 'version_id'])

        # Adding model 'AssemblyStatistics'
        db.create_table(u'samples_assemblystatistics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Sample'])),
            ('is_scaffolds', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.PipelineVersions'])),
            ('total_contig', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('total_contig_length', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('min_contig_length', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('median_contig_length', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('mean_contig_length', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('max_contig_length', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('n50_contig_length', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('l50_contig_count', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('ng50_contig_length', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('lg50_contig_count', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('contigs_greater_1k', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('contigs_greater_10k', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('contigs_greater_100k', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('contigs_greater_1m', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('percent_contigs_greater_1k', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('percent_contigs_greater_10k', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('percent_contigs_greater_100k', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('percent_contigs_greater_1m', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('contig_percent_a', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('contig_percent_t', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('contig_percent_g', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('contig_percent_c', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('contig_percent_n', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('contig_non_acgtn', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('num_contig_non_acgtn', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('samples', ['AssemblyStatistics'])

        # Adding unique constraint on 'AssemblyStatistics', fields ['sample', 'is_scaffolds', 'version']
        db.create_unique(u'samples_assemblystatistics', ['sample_id', 'is_scaffolds', 'version_id'])

        # Adding model 'EnaToSample'
        db.create_table(u'samples_enatosample', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('experiment_accession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.EnaExperiment'], db_column='experiment_accession')),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Sample'])),
        ))
        db.send_create_signal('samples', ['EnaToSample'])

        # Adding unique constraint on 'EnaToSample', fields ['experiment_accession', 'sample']
        db.create_unique(u'samples_enatosample', ['experiment_accession', 'sample_id'])

        # Adding model 'EnaStudy'
        db.create_table(u'samples_enastudy', (
            ('study_accession', self.gf('django.db.models.fields.TextField')(primary_key=True)),
            ('secondary_study_accession', self.gf('django.db.models.fields.TextField')()),
            ('study_title', self.gf('django.db.models.fields.TextField')()),
            ('study_alias', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('samples', ['EnaStudy'])

        # Adding model 'EnaExperiment'
        db.create_table(u'samples_enaexperiment', (
            ('experiment_accession', self.gf('django.db.models.fields.TextField')(primary_key=True)),
            ('experiment_title', self.gf('django.db.models.fields.TextField')()),
            ('experiment_alias', self.gf('django.db.models.fields.TextField')()),
            ('study_accession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.EnaStudy'], db_column='study_accession')),
            ('sample_accession', self.gf('django.db.models.fields.TextField')()),
            ('secondary_sample_accession', self.gf('django.db.models.fields.TextField')()),
            ('submission_accession', self.gf('django.db.models.fields.TextField')()),
            ('tax_id', self.gf('django.db.models.fields.TextField')()),
            ('scientific_name', self.gf('django.db.models.fields.TextField')()),
            ('instrument_platform', self.gf('django.db.models.fields.TextField')(default='', db_index=True)),
            ('instrument_model', self.gf('django.db.models.fields.TextField')()),
            ('library_layout', self.gf('django.db.models.fields.TextField')()),
            ('library_strategy', self.gf('django.db.models.fields.TextField')()),
            ('library_selection', self.gf('django.db.models.fields.TextField')()),
            ('center_name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('samples', ['EnaExperiment'])

        # Adding model 'EnaRun'
        db.create_table(u'samples_enarun', (
            ('run_accession', self.gf('django.db.models.fields.TextField')(primary_key=True)),
            ('experiment_accession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.EnaExperiment'], db_column='experiment_accession')),
            ('is_paired', self.gf('django.db.models.fields.BooleanField')()),
            ('run_alias', self.gf('django.db.models.fields.TextField')()),
            ('read_count', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('base_count', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('mean_read_length', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('coverage', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('first_public', self.gf('django.db.models.fields.TextField')()),
            ('fastq_bytes', self.gf('django.db.models.fields.TextField')()),
            ('fastq_md5', self.gf('django.db.models.fields.TextField')()),
            ('fastq_aspera', self.gf('django.db.models.fields.TextField')()),
            ('fastq_ftp', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('samples', ['EnaRun'])


    def backwards(self, orm):
        # Removing unique constraint on 'EnaToSample', fields ['experiment_accession', 'sample']
        db.delete_unique(u'samples_enatosample', ['experiment_accession', 'sample_id'])

        # Removing unique constraint on 'AssemblyStatistics', fields ['sample', 'is_scaffolds', 'version']
        db.delete_unique(u'samples_assemblystatistics', ['sample_id', 'is_scaffolds', 'version_id'])

        # Removing unique constraint on 'FastqStatistics', fields ['sample', 'is_original', 'version']
        db.delete_unique(u'samples_fastqstatistics', ['sample_id', 'is_original', 'version_id'])

        # Removing unique constraint on 'Programs', fields ['pipeline', 'program', 'version']
        db.delete_unique(u'samples_programs', ['pipeline_id', 'program', 'version'])

        # Removing unique constraint on 'PipelineVersions', fields ['module', 'version']
        db.delete_unique(u'samples_pipelineversions', ['module', 'version'])

        # Deleting model 'Sample'
        db.delete_table(u'samples_sample')

        # Deleting model 'Upload'
        db.delete_table(u'samples_upload')

        # Deleting model 'PipelineVersions'
        db.delete_table(u'samples_pipelineversions')

        # Deleting model 'Programs'
        db.delete_table(u'samples_programs')

        # Deleting model 'FastqStatistics'
        db.delete_table(u'samples_fastqstatistics')

        # Deleting model 'AssemblyStatistics'
        db.delete_table(u'samples_assemblystatistics')

        # Deleting model 'EnaToSample'
        db.delete_table(u'samples_enatosample')

        # Deleting model 'EnaStudy'
        db.delete_table(u'samples_enastudy')

        # Deleting model 'EnaExperiment'
        db.delete_table(u'samples_enaexperiment')

        # Deleting model 'EnaRun'
        db.delete_table(u'samples_enarun')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'samples.assemblystatistics': {
            'Meta': {'unique_together': "(('sample', 'is_scaffolds', 'version'),)", 'object_name': 'AssemblyStatistics'},
            'contig_non_acgtn': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'contig_percent_a': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'contig_percent_c': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'contig_percent_g': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'contig_percent_n': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'contig_percent_t': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'contigs_greater_100k': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'contigs_greater_10k': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'contigs_greater_1k': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'contigs_greater_1m': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_scaffolds': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'l50_contig_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'lg50_contig_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'max_contig_length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'mean_contig_length': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'median_contig_length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'min_contig_length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'n50_contig_length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ng50_contig_length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'num_contig_non_acgtn': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'percent_contigs_greater_100k': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'percent_contigs_greater_10k': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'percent_contigs_greater_1k': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'percent_contigs_greater_1m': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.Sample']"}),
            'total_contig': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'total_contig_length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.PipelineVersions']"})
        },
        'samples.enaexperiment': {
            'Meta': {'object_name': 'EnaExperiment'},
            'center_name': ('django.db.models.fields.TextField', [], {}),
            'experiment_accession': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'experiment_alias': ('django.db.models.fields.TextField', [], {}),
            'experiment_title': ('django.db.models.fields.TextField', [], {}),
            'instrument_model': ('django.db.models.fields.TextField', [], {}),
            'instrument_platform': ('django.db.models.fields.TextField', [], {'default': "''", 'db_index': 'True'}),
            'library_layout': ('django.db.models.fields.TextField', [], {}),
            'library_selection': ('django.db.models.fields.TextField', [], {}),
            'library_strategy': ('django.db.models.fields.TextField', [], {}),
            'sample_accession': ('django.db.models.fields.TextField', [], {}),
            'scientific_name': ('django.db.models.fields.TextField', [], {}),
            'secondary_sample_accession': ('django.db.models.fields.TextField', [], {}),
            'study_accession': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.EnaStudy']", 'db_column': "'study_accession'"}),
            'submission_accession': ('django.db.models.fields.TextField', [], {}),
            'tax_id': ('django.db.models.fields.TextField', [], {})
        },
        'samples.enarun': {
            'Meta': {'object_name': 'EnaRun'},
            'base_count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'coverage': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'experiment_accession': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.EnaExperiment']", 'db_column': "'experiment_accession'"}),
            'fastq_aspera': ('django.db.models.fields.TextField', [], {}),
            'fastq_bytes': ('django.db.models.fields.TextField', [], {}),
            'fastq_ftp': ('django.db.models.fields.TextField', [], {}),
            'fastq_md5': ('django.db.models.fields.TextField', [], {}),
            'first_public': ('django.db.models.fields.TextField', [], {}),
            'is_paired': ('django.db.models.fields.BooleanField', [], {}),
            'mean_read_length': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'read_count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'run_accession': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'run_alias': ('django.db.models.fields.TextField', [], {})
        },
        'samples.enastudy': {
            'Meta': {'object_name': 'EnaStudy'},
            'secondary_study_accession': ('django.db.models.fields.TextField', [], {}),
            'study_accession': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'study_alias': ('django.db.models.fields.TextField', [], {}),
            'study_title': ('django.db.models.fields.TextField', [], {})
        },
        'samples.enatosample': {
            'Meta': {'unique_together': "(('experiment_accession', 'sample'),)", 'object_name': 'EnaToSample'},
            'experiment_accession': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.EnaExperiment']", 'db_column': "'experiment_accession'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.Sample']"})
        },
        'samples.fastqstatistics': {
            'Meta': {'unique_together': "(('sample', 'is_original', 'version'),)", 'object_name': 'FastqStatistics'},
            'coverage': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_original': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'max_read_length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'mean_read_length': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '3'}),
            'min_read_length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'qual_25th': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '3'}),
            'qual_75th': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '3'}),
            'qual_mean': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '3'}),
            'qual_median': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '3'}),
            'qual_std': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '3'}),
            'rank': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.Sample']"}),
            'total_bp': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'total_reads': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.PipelineVersions']"})
        },
        'samples.pipelineversions': {
            'Meta': {'unique_together': "(('module', 'version'),)", 'object_name': 'PipelineVersions'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.TextField', [], {}),
            'version': ('django.db.models.fields.TextField', [], {})
        },
        'samples.programs': {
            'Meta': {'unique_together': "(('pipeline', 'program', 'version'),)", 'object_name': 'Programs'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pipeline': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.PipelineVersions']"}),
            'program': ('django.db.models.fields.TextField', [], {}),
            'version': ('django.db.models.fields.TextField', [], {})
        },
        'samples.sample': {
            'Meta': {'object_name': 'Sample'},
            'clindamycin_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75'}),
            'contact_link': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'daptomycin_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'doi': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'funding_agency': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'funding_agency_link': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'host_age': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'host_gender': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'host_health': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'host_name': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'is_paired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'isolation_city': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'isolation_country': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'isolation_date': ('django.db.models.fields.DateField', [], {'default': "'1900-01-01'", 'blank': 'True'}),
            'isolation_region': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'levofloxacin_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'linezolid_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'oxacillin_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'penicillin_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'publication_link': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'pubmed_id': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'rifampin_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'sample_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample_tag': ('django.db.models.fields.TextField', [], {'default': "''", 'db_index': 'True', 'blank': 'True'}),
            'sequencing_center': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'sequencing_center_link': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'sequencing_date': ('django.db.models.fields.DateField', [], {'default': "'1900-01-01'", 'blank': 'True'}),
            'sequencing_libaray_method': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'sequencing_platform': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'strain': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'tetracycline_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'trimethoprim_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'vancomycin_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'})
        },
        'samples.upload': {
            'Meta': {'object_name': 'Upload'},
            'md5sum': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '32'}),
            'path': ('django.db.models.fields.files.FileField', [], {'default': "''", 'max_length': '100'}),
            'sample': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['samples.Sample']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['samples']