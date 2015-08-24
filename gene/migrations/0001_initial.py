# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.PositiveIntegerField()),
                ('end', models.PositiveIntegerField()),
                ('is_positive', models.BooleanField()),
                ('phase', models.PositiveSmallIntegerField()),
                ('dna', models.TextField()),
                ('aa', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ClusterMembers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member', models.TextField(unique=True)),
                ('entry_name', models.TextField()),
                ('length', models.PositiveIntegerField()),
                ('is_rep', models.BooleanField()),
                ('is_seed', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Clusters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cluster', models.TextField(unique=True)),
                ('dna', models.TextField()),
                ('aa', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Names',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('taxon_id', models.PositiveIntegerField()),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='References',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dna', models.TextField()),
                ('aa', models.TextField()),
            ],
        ),
    ]
