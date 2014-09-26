# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0002_auto_20140925_2300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kmertotal',
            name='sample',
        ),
        migrations.AddField(
            model_name='kmertotal',
            name='kmer',
            field=models.ForeignKey(default=1, to='analysis.Kmer'),
            preserve_default=False,
        ),
    ]
