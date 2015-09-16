# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlst', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='srst2',
            old_name='ST',
            new_name='st',
        ),
    ]
