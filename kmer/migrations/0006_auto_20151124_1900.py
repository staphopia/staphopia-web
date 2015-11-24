# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import kmer.models


class Migration(migrations.Migration):

    dependencies = [
        ('kmer', '0005_auto_20151028_2051'),
    ]

    operations = [
        migrations.CreateModel(
            name='String',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', kmer.models.FixedCharField(unique=True, max_length=31)),
            ],
        ),
        migrations.DeleteModel(
            name='BinaryTmp',
        ),
        migrations.DeleteModel(
            name='CountTemporary',
        ),
        migrations.AlterField(
            model_name='count',
            name='string',
            field=models.ForeignKey(to='kmer.String'),
        ),
        migrations.DeleteModel(
            name='Binary',
        ),
    ]
