# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0013_auto_20150506_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assemblystat',
            name='l50_contig_count',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='assemblystat',
            name='lg50_contig_count',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='assemblystat',
            name='n50_contig_length',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='assemblystat',
            name='ng50_contig_length',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
