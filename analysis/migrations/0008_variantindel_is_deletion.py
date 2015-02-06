# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0007_auto_20150205_0407'),
    ]

    operations = [
        migrations.AddField(
            model_name='variantindel',
            name='is_deletion',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=True,
        ),
    ]
