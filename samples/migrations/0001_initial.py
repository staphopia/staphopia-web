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
            ('sequencing_libaray_method', self.gf('django.db.models.fields.TextField')(default='')),
            ('sequencing_platform', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('publication_link', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
            ('pubmed_id', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('doi', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('funding_agency', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('funding_agency_link', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
            ('strain', self.gf('django.db.models.fields.TextField')(default='')),
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
        db.send_create_signal(u'samples', ['Sample'])

        # Adding model 'Upload'
        db.create_table(u'samples_upload', (
            ('sample', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['samples.Sample'], unique=True, primary_key=True)),
            ('path', self.gf('django.db.models.fields.files.FileField')(default='', max_length=100)),
            ('md5sum', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=32)),
        ))
        db.send_create_signal(u'samples', ['Upload'])


    def backwards(self, orm):
        # Deleting model 'Sample'
        db.delete_table(u'samples_sample')

        # Deleting model 'Upload'
        db.delete_table(u'samples_upload')


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
            'sequencing_libaray_method': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'sequencing_platform': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'strain': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'tetracycline_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'trimethoprim_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'vancomycin_mic': ('django.db.models.fields.DecimalField', [], {'default': '-200.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'})
        },
        u'samples.upload': {
            'Meta': {'object_name': 'Upload'},
            'md5sum': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '32'}),
            'path': ('django.db.models.fields.files.FileField', [], {'default': "''", 'max_length': '100'}),
            'sample': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['samples.Sample']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['samples']