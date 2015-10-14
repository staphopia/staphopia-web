# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gene', '0003_auto_20150923_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='references',
            name='phase',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='references',
            unique_together=set([('reference', 'contig', 'cluster', 'start', 'end')]),
        ),
    ]
