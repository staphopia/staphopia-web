# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SamplesSummary',
            fields=[
            ],
            options={
                'db_table': 'samples_summary',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
