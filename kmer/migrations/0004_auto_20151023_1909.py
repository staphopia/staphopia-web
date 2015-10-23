# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kmer', '0003_auto_20151021_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='count',
            name='string',
            field=models.ForeignKey(to='kmer.Binary'),
        ),
    ]
