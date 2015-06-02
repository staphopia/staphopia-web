# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0014_auto_20150528_1840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='varianttoindel',
            name='info',
        ),
        migrations.RemoveField(
            model_name='varianttosnp',
            name='info',
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='AC',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='AD',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='AF',
            field=models.DecimalField(default=0.0, max_digits=8, decimal_places=3),
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='AN',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='DP',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='GQ',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='GT',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='MQ',
            field=models.DecimalField(default=0.0, max_digits=8, decimal_places=3),
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='PL',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='varianttoindel',
            name='QD',
            field=models.DecimalField(default=0.0, max_digits=8, decimal_places=3),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='AC',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='AD',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='AF',
            field=models.DecimalField(default=0.0, max_digits=8, decimal_places=3),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='AN',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='DP',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='GQ',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='GT',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='MQ',
            field=models.DecimalField(default=0.0, max_digits=8, decimal_places=3),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='PL',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='varianttosnp',
            name='QD',
            field=models.DecimalField(default=0.0, max_digits=8, decimal_places=3),
        ),
        migrations.DeleteModel(
            name='VariantInfo',
        ),
    ]
