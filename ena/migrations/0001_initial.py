# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ToSample'
        db.create_table(u'ena_tosample', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('experiment_accession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ena.Experiment'], db_column='experiment_accession')),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Sample'])),
        ))
        db.send_create_signal(u'ena', ['ToSample'])

        # Adding unique constraint on 'ToSample', fields ['experiment_accession', 'sample']
        db.create_unique(u'ena_tosample', ['experiment_accession', 'sample_id'])

        # Adding model 'Study'
        db.create_table(u'ena_study', (
            ('study_accession', self.gf('django.db.models.fields.TextField')(primary_key=True)),
            ('secondary_study_accession', self.gf('django.db.models.fields.TextField')()),
            ('study_title', self.gf('django.db.models.fields.TextField')()),
            ('study_alias', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'ena', ['Study'])

        # Adding model 'Experiment'
        db.create_table(u'ena_experiment', (
            ('experiment_accession', self.gf('django.db.models.fields.TextField')(primary_key=True)),
            ('experiment_title', self.gf('django.db.models.fields.TextField')()),
            ('experiment_alias', self.gf('django.db.models.fields.TextField')()),
            ('study_accession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ena.Study'], db_column='study_accession')),
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
        db.send_create_signal(u'ena', ['Experiment'])

        # Adding model 'Run'
        db.create_table(u'ena_run', (
            ('run_accession', self.gf('django.db.models.fields.TextField')(primary_key=True)),
            ('experiment_accession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ena.Experiment'], db_column='experiment_accession')),
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
        db.send_create_signal(u'ena', ['Run'])

        # Adding model 'Queue'
        db.create_table(u'ena_queue', (
            ('experiment_accession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ena.Experiment'], primary_key=True, db_column='experiment_accession')),
            ('is_waiting', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'ena', ['Queue'])


    def backwards(self, orm):
        # Removing unique constraint on 'ToSample', fields ['experiment_accession', 'sample']
        db.delete_unique(u'ena_tosample', ['experiment_accession', 'sample_id'])

        # Deleting model 'ToSample'
        db.delete_table(u'ena_tosample')

        # Deleting model 'Study'
        db.delete_table(u'ena_study')

        # Deleting model 'Experiment'
        db.delete_table(u'ena_experiment')

        # Deleting model 'Run'
        db.delete_table(u'ena_run')

        # Deleting model 'Queue'
        db.delete_table(u'ena_queue')


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
        u'ena.experiment': {
            'Meta': {'object_name': 'Experiment'},
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
            'study_accession': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ena.Study']", 'db_column': "'study_accession'"}),
            'submission_accession': ('django.db.models.fields.TextField', [], {}),
            'tax_id': ('django.db.models.fields.TextField', [], {})
        },
        u'ena.queue': {
            'Meta': {'object_name': 'Queue'},
            'experiment_accession': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ena.Experiment']", 'primary_key': 'True', 'db_column': "'experiment_accession'"}),
            'is_waiting': ('django.db.models.fields.BooleanField', [], {})
        },
        u'ena.run': {
            'Meta': {'object_name': 'Run'},
            'base_count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'coverage': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'experiment_accession': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ena.Experiment']", 'db_column': "'experiment_accession'"}),
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
        u'ena.study': {
            'Meta': {'object_name': 'Study'},
            'secondary_study_accession': ('django.db.models.fields.TextField', [], {}),
            'study_accession': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'study_alias': ('django.db.models.fields.TextField', [], {}),
            'study_title': ('django.db.models.fields.TextField', [], {})
        },
        u'ena.tosample': {
            'Meta': {'unique_together': "(('experiment_accession', 'sample'),)", 'object_name': 'ToSample'},
            'experiment_accession': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ena.Experiment']", 'db_column': "'experiment_accession'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Sample']"})
        },
        u'samples.sample': {
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        }
    }

    complete_apps = ['ena']