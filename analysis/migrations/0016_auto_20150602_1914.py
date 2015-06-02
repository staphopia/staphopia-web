# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0015_auto_20150528_2042'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='varianttoindel',
            name='AN',
        ),
        migrations.RemoveField(
            model_name='varianttosnp',
            name='AN',
        ),
    ]
