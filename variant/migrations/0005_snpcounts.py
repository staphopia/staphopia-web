# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('variant', '0004_counts'),
    ]

    operations = [
        migrations.CreateModel(
            name='SNPCounts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField(default=0, db_index=True)),
                ('snp', models.ForeignKey(to='variant.SNP')),
            ],
        ),
    ]
