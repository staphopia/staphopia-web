# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssemblyStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_scaffolds', models.BooleanField(default=False, db_index=True)),
                ('total_contig', models.PositiveSmallIntegerField()),
                ('total_contig_length', models.PositiveIntegerField()),
                ('min_contig_length', models.PositiveIntegerField()),
                ('median_contig_length', models.PositiveIntegerField()),
                ('mean_contig_length', models.DecimalField(max_digits=9, decimal_places=2)),
                ('max_contig_length', models.PositiveIntegerField()),
                ('n50_contig_length', models.PositiveIntegerField()),
                ('l50_contig_count', models.PositiveSmallIntegerField()),
                ('ng50_contig_length', models.PositiveIntegerField()),
                ('lg50_contig_count', models.PositiveSmallIntegerField()),
                ('contigs_greater_1k', models.PositiveSmallIntegerField()),
                ('contigs_greater_10k', models.PositiveSmallIntegerField()),
                ('contigs_greater_100k', models.PositiveSmallIntegerField()),
                ('contigs_greater_1m', models.PositiveSmallIntegerField()),
                ('percent_contigs_greater_1k', models.DecimalField(max_digits=4, decimal_places=2)),
                ('percent_contigs_greater_10k', models.DecimalField(max_digits=4, decimal_places=2)),
                ('percent_contigs_greater_100k', models.DecimalField(max_digits=4, decimal_places=2)),
                ('percent_contigs_greater_1m', models.DecimalField(max_digits=4, decimal_places=2)),
                ('contig_percent_a', models.DecimalField(max_digits=4, decimal_places=2)),
                ('contig_percent_t', models.DecimalField(max_digits=4, decimal_places=2)),
                ('contig_percent_g', models.DecimalField(max_digits=4, decimal_places=2)),
                ('contig_percent_c', models.DecimalField(max_digits=4, decimal_places=2)),
                ('contig_percent_n', models.DecimalField(max_digits=4, decimal_places=2)),
                ('contig_non_acgtn', models.DecimalField(max_digits=4, decimal_places=2)),
                ('num_contig_non_acgtn', models.PositiveSmallIntegerField()),
                ('sample', models.ForeignKey(to='samples.Sample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FastqStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_original', models.BooleanField(default=False, db_index=True)),
                ('rank', models.PositiveSmallIntegerField(db_index=True)),
                ('total_bp', models.PositiveIntegerField()),
                ('total_reads', models.PositiveIntegerField()),
                ('coverage', models.DecimalField(max_digits=6, decimal_places=3)),
                ('min_read_length', models.PositiveIntegerField()),
                ('mean_read_length', models.DecimalField(max_digits=10, decimal_places=3)),
                ('max_read_length', models.PositiveIntegerField()),
                ('qual_mean', models.DecimalField(max_digits=6, decimal_places=3)),
                ('qual_std', models.DecimalField(max_digits=6, decimal_places=3)),
                ('qual_25th', models.DecimalField(max_digits=6, decimal_places=3)),
                ('qual_median', models.DecimalField(max_digits=6, decimal_places=3)),
                ('qual_75th', models.DecimalField(max_digits=6, decimal_places=3)),
                ('sample', models.ForeignKey(to='samples.Sample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Kmer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample', models.ForeignKey(to='samples.Sample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KmerCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField()),
                ('kmer', models.ForeignKey(to='analysis.Kmer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KmerString',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kmer', models.CharField(default=b'', unique=True, max_length=31)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KmerTotal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total', models.PositiveIntegerField()),
                ('sample', models.ForeignKey(to='samples.Sample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PipelineVersions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module', models.TextField()),
                ('version', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Programs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('program', models.TextField()),
                ('version', models.TextField()),
                ('pipeline', models.ForeignKey(to='analysis.PipelineVersions')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='programs',
            unique_together=set([('pipeline', 'program', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='pipelineversions',
            unique_together=set([('module', 'version')]),
        ),
        migrations.AddField(
            model_name='kmercount',
            name='string',
            field=models.ForeignKey(to='analysis.KmerString'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='kmercount',
            unique_together=set([('kmer', 'string')]),
        ),
        migrations.AddField(
            model_name='kmer',
            name='version',
            field=models.ForeignKey(to='analysis.PipelineVersions'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='kmer',
            unique_together=set([('sample', 'version')]),
        ),
        migrations.AddField(
            model_name='fastqstats',
            name='version',
            field=models.ForeignKey(to='analysis.PipelineVersions'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='fastqstats',
            unique_together=set([('sample', 'is_original', 'version')]),
        ),
        migrations.AddField(
            model_name='assemblystats',
            name='version',
            field=models.ForeignKey(to='analysis.PipelineVersions'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='assemblystats',
            unique_together=set([('sample', 'is_scaffolds', 'version')]),
        ),
    ]
