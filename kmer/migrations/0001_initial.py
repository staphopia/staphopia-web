# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Binary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', models.BinaryField(unique=True, max_length=8)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BinaryTmp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', models.BinaryField(unique=True, max_length=8)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Count',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField()),
                ('sample', models.ForeignKey(to='sample.MetaData')),
                ('string', models.ForeignKey(to='kmer.Binary')),
            ],
        ),
        migrations.CreateModel(
            name='Total',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total', models.PositiveIntegerField()),
                ('singletons', models.PositiveIntegerField()),
                ('new_kmers', models.PositiveIntegerField()),
                ('runtime', models.PositiveIntegerField(default=0)),
                ('sample', models.ForeignKey(to='sample.MetaData')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='count',
            unique_together=set([('sample', 'string')]),
        ),
    ]
