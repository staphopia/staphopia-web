# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kmer', '0003_auto_20150821_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='binary',
            name='string',
            field=models.BinaryField(unique=True, max_length=8),
        ),
        migrations.AlterField(
            model_name='binarytmp',
            name='string',
            field=models.BinaryField(unique=True, max_length=8),
        ),
    ]
