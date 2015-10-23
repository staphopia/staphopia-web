# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kmer', '0002_binarytemporary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='binarytemporary',
            name='string',
            field=models.BinaryField(unique=True, max_length=8),
        ),
        migrations.AlterField(
            model_name='count',
            name='string',
            field=models.ForeignKey(to='kmer.BinaryTemporary'),
        ),
    ]
