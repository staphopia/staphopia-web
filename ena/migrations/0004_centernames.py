# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ena', '0003_googlescholar'),
    ]

    operations = [
        migrations.CreateModel(
            name='CenterNames',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ena_name', models.TextField()),
                ('name', models.TextField()),
            ],
        ),
    ]
