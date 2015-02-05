# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0001_initial'),
        ('analysis', '0005_auto_20150203_2024'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssemblyStat',
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
            name='FastqStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_original', models.BooleanField(default=False, db_index=True)),
                ('rank', models.PositiveSmallIntegerField(db_index=True)),
                ('total_bp', models.BigIntegerField()),
                ('total_reads', models.BigIntegerField()),
                ('coverage', models.DecimalField(max_digits=7, decimal_places=2)),
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
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('program', models.TextField()),
                ('version', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='PipelineVersions',
            new_name='PipelineVersion',
        ),
        migrations.AlterUniqueTogether(
            name='assemblystats',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='assemblystats',
            name='sample',
        ),
        migrations.RemoveField(
            model_name='assemblystats',
            name='version',
        ),
        migrations.DeleteModel(
            name='AssemblyStats',
        ),
        migrations.AlterUniqueTogether(
            name='fastqstats',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='fastqstats',
            name='sample',
        ),
        migrations.RemoveField(
            model_name='fastqstats',
            name='version',
        ),
        migrations.DeleteModel(
            name='FastqStats',
        ),
        migrations.AlterUniqueTogether(
            name='programs',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='programs',
            name='pipeline',
        ),
        migrations.DeleteModel(
            name='Programs',
        ),
        migrations.AddField(
            model_name='program',
            name='pipeline',
            field=models.ForeignKey(to='analysis.PipelineVersion'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='program',
            unique_together=set([('pipeline', 'program', 'version')]),
        ),
        migrations.AddField(
            model_name='fastqstat',
            name='version',
            field=models.ForeignKey(to='analysis.PipelineVersion'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='fastqstat',
            unique_together=set([('sample', 'is_original', 'version')]),
        ),
        migrations.AddField(
            model_name='assemblystat',
            name='version',
            field=models.ForeignKey(to='analysis.PipelineVersion'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='assemblystat',
            unique_together=set([('sample', 'is_scaffolds', 'version')]),
        ),
    ]
