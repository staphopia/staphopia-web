# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gene', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='references',
            name='end',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='references',
            name='is_positive',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='references',
            name='is_tRNA',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='references',
            name='start',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
