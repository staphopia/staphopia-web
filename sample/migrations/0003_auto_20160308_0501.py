# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0002_auto_20151005_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='project_tag',
            field=models.TextField(default=b'', db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='sample_tag',
            field=models.TextField(unique=True),
        ),
    ]
