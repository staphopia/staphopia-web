# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gene', '0003_auto_20150827_2038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clusters',
            old_name='cluster',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='clusters',
            name='dna',
        ),
    ]
