# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('variant', '0005_snpcounts'),
        ('gene', '0004_auto_20151014_0208'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceSequence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(db_index=True)),
                ('sequence', models.TextField()),
                ('reference', models.ForeignKey(to='variant.Reference')),
            ],
        ),
        migrations.AlterField(
            model_name='references',
            name='contig',
            field=models.ForeignKey(default=0, to='gene.ReferenceSequence'),
        ),
        migrations.AlterUniqueTogether(
            name='referencesequence',
            unique_together=set([('reference', 'name')]),
        ),
    ]
