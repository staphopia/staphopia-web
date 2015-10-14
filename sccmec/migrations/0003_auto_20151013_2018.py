# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sccmec', '0002_auto_20151013_2003'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cassette',
            unique_together=set([('name', 'header')]),
        ),
        migrations.AlterUniqueTogether(
            name='coverage',
            unique_together=set([('sample', 'cassette')]),
        ),
    ]
