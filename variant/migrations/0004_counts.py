# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0001_initial'),
        ('variant', '0003_auto_20150913_0553'),
    ]

    operations = [
        migrations.CreateModel(
            name='Counts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('snp', models.PositiveIntegerField(default=0)),
                ('indel', models.PositiveIntegerField(default=0)),
                ('confidence', models.PositiveIntegerField(default=0)),
                ('sample', models.ForeignKey(to='sample.MetaData')),
            ],
        ),
    ]
