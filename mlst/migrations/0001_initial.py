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
            name='Blast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('locus_name', models.CharField(max_length=4)),
                ('locus_id', models.PositiveSmallIntegerField()),
                ('bitscore', models.PositiveSmallIntegerField()),
                ('slen', models.PositiveSmallIntegerField()),
                ('length', models.PositiveSmallIntegerField()),
                ('gaps', models.PositiveSmallIntegerField()),
                ('mismatch', models.PositiveSmallIntegerField()),
                ('pident', models.DecimalField(max_digits=5, decimal_places=2)),
                ('evalue', models.DecimalField(max_digits=7, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='MLST',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample', models.ForeignKey(related_name='mlst_sample_id', to='samples.Sample')),
                ('version', models.ForeignKey(related_name='mlst_version_id', to='analysis.PipelineVersion')),
            ],
        ),
        migrations.CreateModel(
            name='SequenceTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ST', models.PositiveIntegerField(unique=True)),
                ('arcc', models.PositiveIntegerField()),
                ('aroe', models.PositiveIntegerField()),
                ('glpf', models.PositiveIntegerField()),
                ('gmk', models.PositiveIntegerField()),
                ('pta', models.PositiveIntegerField()),
                ('tpi', models.PositiveIntegerField()),
                ('yqil', models.PositiveIntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Srst2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ST', models.TextField()),
                ('arcc', models.TextField()),
                ('aroe', models.TextField()),
                ('glpf', models.TextField()),
                ('gmk', models.TextField()),
                ('pta', models.TextField()),
                ('tpi', models.TextField()),
                ('yqil', models.TextField()),
                ('mismatches', models.TextField()),
                ('uncertainty', models.TextField()),
                ('depth', models.DecimalField(max_digits=8, decimal_places=3)),
                ('maxMAF', models.DecimalField(max_digits=11, decimal_places=7)),
                ('mlst', models.ForeignKey(to='mlst.MLST')),
            ],
        ),
        migrations.AddField(
            model_name='blast',
            name='mlst',
            field=models.ForeignKey(to='mlst.MLST'),
        ),
        migrations.AlterUniqueTogether(
            name='mlst',
            unique_together=set([('sample', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='blast',
            unique_together=set([('mlst', 'locus_name', 'locus_id')]),
        ),
    ]
