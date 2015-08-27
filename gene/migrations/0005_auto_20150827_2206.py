# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gene', '0004_auto_20150827_2138'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='features',
            unique_together=set([('sample', 'version', 'contig', 'cluster', 'start', 'end')]),
        ),
    ]
