# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0003_auto_20150506_2138'),
        ('analysis', '0018_auto_20150715_1758'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.PositiveIntegerField()),
                ('end', models.PositiveIntegerField()),
                ('is_positive', models.BooleanField()),
                ('locus_tag', models.CharField(max_length=24)),
                ('protein_id', models.CharField(max_length=24)),
                ('gene', models.CharField(max_length=12)),
                ('db_xref', models.TextField()),
                ('product', models.TextField()),
                ('note', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(unique=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Confidence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('AC', models.TextField(default=b'')),
                ('AD', models.TextField(default=b'')),
                ('AF', models.DecimalField(default=0.0, max_digits=8, decimal_places=3)),
                ('DP', models.PositiveIntegerField(default=0)),
                ('GQ', models.PositiveIntegerField(default=0)),
                ('GT', models.TextField(default=b'')),
                ('MQ', models.DecimalField(default=0.0, max_digits=8, decimal_places=3)),
                ('PL', models.TextField(default=b'')),
                ('QD', models.DecimalField(default=0.0, max_digits=8, decimal_places=3)),
                ('quality', models.DecimalField(max_digits=8, decimal_places=3)),
            ],
        ),
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Indel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_position', models.PositiveIntegerField(db_index=True)),
                ('reference_base', models.TextField()),
                ('alternate_base', models.TextField()),
                ('is_deletion', models.BooleanField(default=False, db_index=True)),
                ('annotation', models.ForeignKey(to='variant.Annotation')),
            ],
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='SNP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_position', models.PositiveIntegerField(db_index=True)),
                ('reference_base', models.CharField(max_length=1)),
                ('alternate_base', models.CharField(max_length=1)),
                ('reference_codon', models.CharField(max_length=3)),
                ('alternate_codon', models.CharField(max_length=3)),
                ('reference_amino_acid', models.CharField(max_length=1)),
                ('alternate_amino_acid', models.CharField(max_length=1)),
                ('codon_position', models.PositiveIntegerField()),
                ('snp_codon_position', models.PositiveSmallIntegerField()),
                ('amino_acid_change', models.TextField()),
                ('is_synonymous', models.PositiveSmallIntegerField()),
                ('is_transition', models.PositiveSmallIntegerField()),
                ('is_genic', models.PositiveSmallIntegerField()),
                ('annotation', models.ForeignKey(to='variant.Annotation')),
                ('reference', models.ForeignKey(to='variant.Reference')),
            ],
        ),
        migrations.CreateModel(
            name='ToIndel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('confidence', models.ForeignKey(to='variant.Confidence')),
                ('filters', models.ForeignKey(to='variant.Filter')),
                ('indel', models.ForeignKey(to='variant.Indel')),
            ],
        ),
        migrations.CreateModel(
            name='ToSNP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.ForeignKey(to='variant.Comment')),
                ('confidence', models.ForeignKey(to='variant.Confidence')),
                ('filters', models.ForeignKey(to='variant.Filter')),
                ('snp', models.ForeignKey(to='variant.SNP')),
            ],
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample', models.ForeignKey(related_name='variant_sample_id', to='samples.Sample')),
                ('version', models.ForeignKey(related_name='variant_version_id', to='analysis.PipelineVersion')),
            ],
        ),
        migrations.AddField(
            model_name='tosnp',
            name='variant',
            field=models.ForeignKey(to='variant.Variant'),
        ),
        migrations.AddField(
            model_name='toindel',
            name='variant',
            field=models.ForeignKey(to='variant.Variant'),
        ),
        migrations.AddField(
            model_name='indel',
            name='reference',
            field=models.ForeignKey(to='variant.Reference'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='reference',
            field=models.ForeignKey(to='variant.Reference'),
        ),
        migrations.AlterUniqueTogether(
            name='variant',
            unique_together=set([('sample', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='tosnp',
            unique_together=set([('variant', 'snp')]),
        ),
        migrations.AlterUniqueTogether(
            name='toindel',
            unique_together=set([('variant', 'indel')]),
        ),
        migrations.AlterUniqueTogether(
            name='snp',
            unique_together=set([('reference', 'reference_position', 'reference_base', 'alternate_base')]),
        ),
        migrations.AlterUniqueTogether(
            name='indel',
            unique_together=set([('reference', 'reference_position', 'reference_base', 'alternate_base')]),
        ),
    ]
