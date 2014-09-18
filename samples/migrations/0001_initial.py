# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import samples.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample_tag', models.TextField(default=b'', db_index=True, blank=True)),
                ('contact_name', models.TextField(default=b'')),
                ('contact_email', models.EmailField(default=b'', max_length=75)),
                ('contact_link', models.URLField(default=b'', blank=True)),
                ('sequencing_center', models.TextField(default=b'')),
                ('sequencing_center_link', models.URLField(default=b'', blank=True)),
                ('sequencing_date', models.DateField(default=b'1900-01-01', blank=True)),
                ('sequencing_libaray_method', models.TextField(default=b'', blank=True)),
                ('sequencing_platform', models.TextField(default=b'', blank=True)),
                ('publication_link', models.URLField(default=b'', blank=True)),
                ('pubmed_id', models.TextField(default=b'', blank=True)),
                ('doi', models.TextField(default=b'', blank=True)),
                ('funding_agency', models.TextField(default=b'', blank=True)),
                ('funding_agency_link', models.URLField(default=b'', blank=True)),
                ('strain', models.TextField(default=b'', blank=True)),
                ('isolation_date', models.DateField(default=b'1900-01-01', blank=True)),
                ('isolation_country', models.TextField(default=b'', blank=True)),
                ('isolation_city', models.TextField(default=b'', blank=True)),
                ('isolation_region', models.TextField(default=b'', blank=True)),
                ('host_name', models.TextField(default=b'', blank=True)),
                ('host_health', models.TextField(default=b'', blank=True)),
                ('host_age', models.PositiveSmallIntegerField(default=0, blank=True)),
                ('host_gender', models.TextField(default=b'', blank=True)),
                ('comments', models.TextField(default=b'', blank=True)),
                ('vancomycin_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('penicillin_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('oxacillin_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('clindamycin_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('daptomycin_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('levofloxacin_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('linezolid_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('rifampin_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('tetracycline_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('trimethoprim_mic', models.DecimalField(default=-200.0, max_digits=6, decimal_places=3, blank=True)),
                ('source', models.TextField(default=b'', blank=True)),
                ('is_public', models.BooleanField(default=True, db_index=True)),
                ('is_paired', models.BooleanField(default=False)),
                ('is_published', models.BooleanField(default=False, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('sample', models.OneToOneField(primary_key=True, serialize=False, to='samples.Sample')),
                ('path', models.FileField(default=b'', upload_to=samples.models.content_file_name)),
                ('md5sum', models.CharField(default=b'', unique=True, max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sample',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
