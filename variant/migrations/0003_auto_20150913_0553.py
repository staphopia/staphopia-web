# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0001_initial'),
        ('variant', '0002_auto_20150913_0422'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toindel',
            name='confidence',
        ),
        migrations.RemoveField(
            model_name='tosnp',
            name='confidence',
        ),
        migrations.AddField(
            model_name='confidence',
            name='reference_position',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='confidence',
            name='sample',
            field=models.ForeignKey(default=0, to='sample.MetaData'),
            preserve_default=False,
        ),
    ]
