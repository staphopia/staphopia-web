# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('experiment_accession', models.TextField(serialize=False, primary_key=True)),
                ('experiment_title', models.TextField()),
                ('experiment_alias', models.TextField()),
                ('sample_accession', models.TextField()),
                ('secondary_sample_accession', models.TextField()),
                ('submission_accession', models.TextField()),
                ('tax_id', models.TextField()),
                ('scientific_name', models.TextField()),
                ('instrument_platform', models.TextField(default=b'', db_index=True)),
                ('instrument_model', models.TextField()),
                ('library_layout', models.TextField()),
                ('library_strategy', models.TextField()),
                ('library_selection', models.TextField()),
                ('center_name', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('run_accession', models.TextField(serialize=False, primary_key=True)),
                ('is_paired', models.BooleanField(default=False)),
                ('run_alias', models.TextField()),
                ('read_count', models.BigIntegerField()),
                ('base_count', models.BigIntegerField()),
                ('mean_read_length', models.DecimalField(max_digits=10, decimal_places=2)),
                ('coverage', models.DecimalField(max_digits=10, decimal_places=2)),
                ('first_public', models.TextField()),
                ('fastq_bytes', models.TextField()),
                ('fastq_md5', models.TextField()),
                ('fastq_aspera', models.TextField()),
                ('fastq_ftp', models.TextField()),
                ('experiment_accession', models.ForeignKey(to='ena.Experiment', db_column=b'experiment_accession')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('study_accession', models.TextField(serialize=False, primary_key=True)),
                ('secondary_study_accession', models.TextField()),
                ('study_title', models.TextField()),
                ('study_alias', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ToSample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('experiment_accession', models.ForeignKey(to='ena.Experiment', db_column=b'experiment_accession')),
                ('sample', models.ForeignKey(to='samples.Sample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tosample',
            unique_together=set([('experiment_accession', 'sample')]),
        ),
        migrations.AddField(
            model_name='experiment',
            name='study_accession',
            field=models.ForeignKey(to='ena.Study', db_column=b'study_accession'),
            preserve_default=True,
        ),
    ]
