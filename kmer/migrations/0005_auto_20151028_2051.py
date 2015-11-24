# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kmer', '0004_auto_20151023_1909'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountTemporary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample_id', models.IntegerField()),
                ('string_id', models.BigIntegerField()),
                ('count', models.IntegerField()),
            ],
        ),
    ]
