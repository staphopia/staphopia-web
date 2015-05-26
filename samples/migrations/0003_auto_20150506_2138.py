# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0002_samplessummary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='contact_email',
            field=models.EmailField(default=b'', max_length=254),
        ),
    ]
