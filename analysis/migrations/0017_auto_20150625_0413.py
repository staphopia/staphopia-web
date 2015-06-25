# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0016_auto_20150602_1914'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='kmer',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='kmer',
            name='sample',
        ),
        migrations.RemoveField(
            model_name='kmer',
            name='version',
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
        migrations.RemoveField(
            model_name='kmertotal',
            name='kmer',
        ),
        migrations.DeleteModel(
            name='Kmer',
        ),
        migrations.DeleteModel(
            name='KmerCount',
        ),
        migrations.DeleteModel(
            name='KmerString',
        ),
        migrations.DeleteModel(
            name='KmerTotal',
        ),
    ]
