# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0010_auto_20150206_0333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mlst',
            name='blast_st',
        ),
    ]
