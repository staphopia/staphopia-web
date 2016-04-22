# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 12:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gene', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contigs',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='contigs',
            name='sample',
        ),
        migrations.AlterField(
            model_name='features',
            name='contig',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='assembly.Contigs'),
        ),
        migrations.DeleteModel(
            name='Contigs',
        ),
    ]