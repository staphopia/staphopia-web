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
            name='Stats',
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
                ('version', models.ForeignKey(to='analysis.PipelineVersion')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='stats',
            unique_together=set([('sample', 'is_original', 'version')]),
        ),
    ]
