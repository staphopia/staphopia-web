# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import kmer.models


class Migration(migrations.Migration):

    dependencies = [
        ('kmer', '0006_auto_20151124_1900'),
    ]

    operations = [
        migrations.CreateModel(
            name='StringTmp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', kmer.models.FixedCharField(unique=True, max_length=31)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
