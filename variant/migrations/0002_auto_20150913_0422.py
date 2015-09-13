# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('variant', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotation',
            name='end',
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='is_positive',
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='start',
        ),
    ]
