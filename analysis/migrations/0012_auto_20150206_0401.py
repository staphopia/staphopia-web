# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0011_remove_mlst_blast_st'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mlstblast',
            old_name='loci_id',
            new_name='locus_id',
        ),
        migrations.RenameField(
            model_name='mlstblast',
            old_name='loci_name',
            new_name='locus_name',
        ),
        migrations.AlterUniqueTogether(
            name='mlstblast',
            unique_together=set([('mlst', 'locus_name', 'locus_id')]),
        ),
    ]
