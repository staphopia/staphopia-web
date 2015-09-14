# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ena', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pmid', models.TextField()),
                ('experiment_accession', models.ForeignKey(to='ena.Experiment', db_column=b'experiment_accession')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='publication',
            unique_together=set([('experiment_accession', 'pmid')]),
        ),
    ]
