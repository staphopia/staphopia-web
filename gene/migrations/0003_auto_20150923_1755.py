# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gene', '0002_auto_20150913_0422'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='references',
            name='annotation',
        ),
        migrations.AddField(
            model_name='references',
            name='contig',
            field=models.ForeignKey(default=0, to='gene.Contigs'),
        ),
        migrations.AlterField(
            model_name='features',
            name='contig',
            field=models.ForeignKey(default=0, to='gene.Contigs'),
        ),
    ]
