# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0012_auto_20150206_0401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mlstsrst2',
            name='mlst',
            field=models.ForeignKey(to='analysis.MLST'),
        ),
    ]
