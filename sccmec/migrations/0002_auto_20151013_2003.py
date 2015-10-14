# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sccmec', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coverage',
            name='maximum',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='coverage',
            name='median',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='coverage',
            name='minimum',
            field=models.PositiveIntegerField(),
        ),
    ]
