# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0008_variantindel_is_deletion'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='varianttoindel',
            unique_together=set([('variant', 'indel')]),
        ),
        migrations.AlterUniqueTogether(
            name='varianttosnp',
            unique_together=set([('variant', 'snp')]),
        ),
    ]
