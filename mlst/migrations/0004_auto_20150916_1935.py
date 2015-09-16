# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlst', '0003_auto_20150916_1855'),
    ]

    operations = [
        migrations.RenameField(
            model_name='srst2',
            old_name='st',
            new_name='st_original',
        ),
        migrations.AddField(
            model_name='srst2',
            name='is_exact',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AddField(
            model_name='srst2',
            name='st_stripped',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
    ]
