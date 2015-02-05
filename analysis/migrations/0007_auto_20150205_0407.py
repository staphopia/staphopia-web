# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0001_initial'),
        ('analysis', '0006_auto_20150204_2254'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample', models.ForeignKey(to='samples.Sample')),
                ('version', models.ForeignKey(to='analysis.PipelineVersion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariantAnnotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('locus_tag', models.CharField(max_length=24)),
                ('protein_id', models.CharField(max_length=24)),
                ('gene', models.CharField(max_length=12)),
                ('db_xref', models.TextField()),
                ('product', models.TextField()),
                ('note', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariantComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(unique=True, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariantFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariantIndel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_position', models.PositiveIntegerField()),
                ('reference_base', models.TextField()),
                ('alternate_base', models.TextField()),
                ('annotation', models.ForeignKey(to='analysis.VariantAnnotation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariantInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('AC', models.TextField()),
                ('AD', models.TextField()),
                ('AF', models.DecimalField(max_digits=8, decimal_places=3)),
                ('AN', models.PositiveIntegerField()),
                ('DP', models.PositiveIntegerField()),
                ('GQ', models.PositiveIntegerField()),
                ('GT', models.TextField()),
                ('MQ', models.DecimalField(max_digits=8, decimal_places=3)),
                ('PL', models.TextField()),
                ('QD', models.DecimalField(max_digits=8, decimal_places=3)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariantReference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariantSNP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_position', models.PositiveIntegerField()),
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
                ('annotation', models.ForeignKey(to='analysis.VariantAnnotation')),
                ('reference', models.ForeignKey(to='analysis.VariantReference')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariantToIndel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quality', models.DecimalField(max_digits=8, decimal_places=3)),
                ('filters', models.ForeignKey(to='analysis.VariantFilter')),
                ('indel', models.ForeignKey(to='analysis.VariantIndel')),
                ('info', models.ForeignKey(to='analysis.VariantInfo')),
                ('variant', models.ForeignKey(to='analysis.Variant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariantToSNP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quality', models.DecimalField(max_digits=8, decimal_places=3)),
                ('comment', models.ForeignKey(to='analysis.VariantComment')),
                ('filters', models.ForeignKey(to='analysis.VariantFilter')),
                ('info', models.ForeignKey(to='analysis.VariantInfo')),
                ('snp', models.ForeignKey(to='analysis.VariantSNP')),
                ('variant', models.ForeignKey(to='analysis.Variant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='variantsnp',
            unique_together=set([('reference', 'reference_position', 'reference_base', 'alternate_base')]),
        ),
        migrations.AddField(
            model_name='variantindel',
            name='reference',
            field=models.ForeignKey(to='analysis.VariantReference'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='variantindel',
            unique_together=set([('reference', 'reference_position', 'reference_base', 'alternate_base')]),
        ),
        migrations.AddField(
            model_name='variantannotation',
            name='reference',
            field=models.ForeignKey(to='analysis.VariantReference'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='variant',
            unique_together=set([('sample', 'version')]),
        ),
    ]
