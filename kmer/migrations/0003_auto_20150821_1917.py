# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kmer', '0002_kmertotal_runtime'),
    ]

    operations = [
        migrations.CreateModel(
            name='Count',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField()),
                ('kmer', models.ForeignKey(to='kmer.Kmer')),
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
                ('kmer', models.ForeignKey(to='kmer.Kmer')),
            ],
        ),
        migrations.RenameModel(
            old_name='KmerBinary',
            new_name='Binary',
        ),
        migrations.RenameModel(
            old_name='KmerBinaryTmp',
            new_name='BinaryTmp',
        ),
        migrations.AlterUniqueTogether(
            name='kmercount',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='kmercount',
            name='kmer',
        ),
        migrations.RemoveField(
            model_name='kmercount',
            name='string',
        ),
        migrations.DeleteModel(
            name='KmerString',
        ),
        migrations.RemoveField(
            model_name='kmertotal',
            name='kmer',
        ),
        migrations.DeleteModel(
            name='KmerCount',
        ),
        migrations.DeleteModel(
            name='KmerTotal',
        ),
        migrations.AddField(
            model_name='count',
            name='string',
            field=models.ForeignKey(to='kmer.Binary'),
        ),
        migrations.AlterUniqueTogether(
            name='count',
            unique_together=set([('kmer', 'string')]),
        ),
    ]
