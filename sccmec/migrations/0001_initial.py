# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0002_auto_20151005_1758'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cassette',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('header', models.TextField()),
                ('length', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Coverage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total', models.DecimalField(max_digits=5, decimal_places=2)),
                ('minimum', models.DecimalField(max_digits=5, decimal_places=2)),
                ('mean', models.DecimalField(max_digits=5, decimal_places=2)),
                ('median', models.DecimalField(max_digits=5, decimal_places=2)),
                ('maximum', models.DecimalField(max_digits=5, decimal_places=2)),
                ('cassette', models.ForeignKey(to='sccmec.Cassette')),
                ('sample', models.ForeignKey(to='sample.MetaData')),
            ],
        ),
    ]
