# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-22 02:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0003_program'),
        ('kmer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Count',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string_id', models.PositiveIntegerField()),
                ('count', models.PositiveIntegerField()),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sample.MetaData')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='count',
            unique_together=set([('sample', 'string_id')]),
        ),
    ]