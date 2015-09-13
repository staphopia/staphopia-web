# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_scaffolds', models.BooleanField(default=False, db_index=True)),
                ('total_contig', models.PositiveSmallIntegerField()),
                ('total_contig_length', models.PositiveIntegerField()),
                ('min_contig_length', models.PositiveIntegerField()),
                ('median_contig_length', models.PositiveIntegerField()),
                ('mean_contig_length', models.DecimalField(max_digits=9, decimal_places=2)),
                ('max_contig_length', models.PositiveIntegerField()),
                ('n50_contig_length', models.PositiveIntegerField(default=0)),
                ('l50_contig_count', models.PositiveSmallIntegerField(default=0)),
                ('ng50_contig_length', models.PositiveIntegerField(default=0)),
                ('lg50_contig_count', models.PositiveSmallIntegerField(default=0)),
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
                ('sample', models.ForeignKey(to='sample.MetaData')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='stats',
            unique_together=set([('sample', 'is_scaffolds')]),
        ),
    ]
