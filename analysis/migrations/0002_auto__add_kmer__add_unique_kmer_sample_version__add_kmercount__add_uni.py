# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Kmer'
        db.create_table(u'analysis_kmer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Sample'])),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.PipelineVersions'])),
        ))
        db.send_create_signal(u'analysis', ['Kmer'])

        # Adding unique constraint on 'Kmer', fields ['sample', 'version']
        db.create_unique(u'analysis_kmer', ['sample_id', 'version_id'])

        # Adding model 'KmerCount'
        db.create_table(u'analysis_kmercount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kmer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Kmer'])),
            ('string', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.KmerString'])),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'analysis', ['KmerCount'])

        # Adding unique constraint on 'KmerCount', fields ['kmer', 'string']
        db.create_unique(u'analysis_kmercount', ['kmer_id', 'string_id'])

        # Adding model 'KmerString'
        db.create_table(u'analysis_kmerstring', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kmer', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=31)),
        ))
        db.send_create_signal(u'analysis', ['KmerString'])

        # Adding model 'KmerTotal'
        db.create_table(u'analysis_kmertotal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Sample'])),
            ('total', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'analysis', ['KmerTotal'])


    def backwards(self, orm):
        # Removing unique constraint on 'KmerCount', fields ['kmer', 'string']
        db.delete_unique(u'analysis_kmercount', ['kmer_id', 'string_id'])

        # Removing unique constraint on 'Kmer', fields ['sample', 'version']
        db.delete_unique(u'analysis_kmer', ['sample_id', 'version_id'])

        # Deleting model 'Kmer'
        db.delete_table(u'analysis_kmer')

        # Deleting model 'KmerCount'
        db.delete_table(u'analysis_kmercount')

        # Deleting model 'KmerString'
        db.delete_table(u'analysis_kmerstring')

        # Deleting model 'KmerTotal'
        db.delete_table(u'analysis_kmertotal')


    models = {
        u'analysis.assemblystats': {
            'Meta': {'unique_together': "(('sample', 'is_scaffolds', 'version'),)", 'object_name': 'AssemblyStats'},
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
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Sample']"}),
            'total_contig': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'total_contig_length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['analysis.PipelineVersions']"})
        },
        u'analysis.fastqstats': {
            'Meta': {'unique_together': "(('sample', 'is_original', 'version'),)", 'object_name': 'FastqStats'},
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
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Sample']"}),
            'total_bp': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'total_reads': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['analysis.PipelineVersions']"})
        },
        u'analysis.kmer': {
            'Meta': {'unique_together': "(('sample', 'version'),)", 'object_name': 'Kmer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Sample']"}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['analysis.PipelineVersions']"})
        },
        u'analysis.kmercount': {
            'Meta': {'unique_together': "(('kmer', 'string'),)", 'object_name': 'KmerCount'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kmer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['analysis.Kmer']"}),
            'string': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['analysis.KmerString']"})
        },
        u'analysis.kmerstring': {
            'Meta': {'object_name': 'KmerString'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kmer': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '31'})
        },
        u'analysis.kmertotal': {
            'Meta': {'object_name': 'KmerTotal'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Sample']"}),
            'total': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'analysis.pipelineversions': {
            'Meta': {'unique_together': "(('module', 'version'),)", 'object_name': 'PipelineVersions'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.TextField', [], {}),
            'version': ('django.db.models.fields.TextField', [], {})
        },
        u'analysis.programs': {
            'Meta': {'unique_together': "(('pipeline', 'program', 'version'),)", 'object_name': 'Programs'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pipeline': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['analysis.PipelineVersions']"}),
            'program': ('django.db.models.fields.TextField', [], {}),
            'version': ('django.db.models.fields.TextField', [], {})
        },
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

    complete_apps = ['analysis']