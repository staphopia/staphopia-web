# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlst', '0002_auto_20150916_1854'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sequencetypes',
            old_name='ST',
            new_name='st',
        ),
    ]
