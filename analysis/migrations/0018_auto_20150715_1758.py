# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0017_auto_20150625_0413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variantindel',
            name='reference_position',
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='variantsnp',
            name='reference_position',
            field=models.PositiveIntegerField(db_index=True),
        ),
    ]
