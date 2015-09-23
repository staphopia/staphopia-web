# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ena', '0002_auto_20150914_2027'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleScholar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accession', models.TextField(db_index=True)),
                ('title', models.TextField()),
                ('url', models.TextField()),
                ('cluster_id', models.TextField()),
                ('url_citations', models.TextField()),
            ],
        ),
    ]
