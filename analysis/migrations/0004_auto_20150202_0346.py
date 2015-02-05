# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0003_auto_20140925_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kmerstring',
            name='string',
            field=models.CharField(default=b'', unique=True, max_length=31, db_index=True),
        ),
    ]
