# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0003_auto_20150506_2138'),
        ('analysis', '0017_auto_20150625_0413'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kmer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample', models.ForeignKey(to='samples.Sample')),
                ('version', models.ForeignKey(to='analysis.PipelineVersion')),
            ],
        ),
        migrations.CreateModel(
            name='KmerBinary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', models.BinaryField(unique=True, max_length=8, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KmerBinaryTmp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', models.BinaryField(unique=True, max_length=8, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KmerCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField()),
                ('kmer', models.ForeignKey(to='kmer.Kmer')),
                ('string', models.ForeignKey(to='kmer.KmerBinary')),
            ],
        ),
        migrations.CreateModel(
            name='KmerString',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', models.CharField(default=b'', unique=True, max_length=31, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='KmerTotal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total', models.PositiveIntegerField()),
                ('singletons', models.PositiveIntegerField()),
                ('new_kmers', models.PositiveIntegerField()),
                ('kmer', models.ForeignKey(to='kmer.Kmer')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='kmercount',
            unique_together=set([('kmer', 'string')]),
        ),
        migrations.AlterUniqueTogether(
            name='kmer',
            unique_together=set([('sample', 'version')]),
        ),
    ]
