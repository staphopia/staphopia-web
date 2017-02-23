# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-23 18:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ena', '0003_auto_20170220_1859'),
    ]

    operations = [
        migrations.CreateModel(
            name='BioSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accession', models.TextField(unique=True)),
                ('secondary_sample_accession', models.TextField(unique=True)),
                ('bio_material', models.TextField()),
                ('cell_line', models.TextField()),
                ('cell_type', models.TextField()),
                ('collected_by', models.TextField()),
                ('collection_date', models.TextField()),
                ('country', models.TextField()),
                ('cultivar', models.TextField()),
                ('culture_collection', models.TextField()),
                ('description', models.TextField()),
                ('dev_stage', models.TextField()),
                ('ecotype', models.TextField()),
                ('environmental_sample', models.TextField()),
                ('first_public', models.TextField()),
                ('germline', models.TextField()),
                ('identified_by', models.TextField()),
                ('isolate', models.TextField()),
                ('isolation_source', models.TextField()),
                ('location', models.TextField()),
                ('mating_type', models.TextField()),
                ('serotype', models.TextField()),
                ('serovar', models.TextField()),
                ('sex', models.TextField()),
                ('submitted_sex', models.TextField()),
                ('specimen_voucher', models.TextField()),
                ('strain', models.TextField()),
                ('sub_species', models.TextField()),
                ('sub_strain', models.TextField()),
                ('tissue_lib', models.TextField()),
                ('tissue_type', models.TextField()),
                ('variety', models.TextField()),
                ('tax_id', models.TextField()),
                ('scientific_name', models.TextField()),
                ('sample_alias', models.TextField()),
                ('checklist', models.TextField()),
                ('center_name', models.TextField()),
                ('depth', models.TextField()),
                ('elevation', models.TextField()),
                ('altitude', models.TextField()),
                ('environment_biome', models.TextField()),
                ('environment_feature', models.TextField()),
                ('environment_material', models.TextField()),
                ('temperature', models.TextField()),
                ('salinity', models.TextField()),
                ('sampling_campaign', models.TextField()),
                ('sampling_site', models.TextField()),
                ('sampling_platform', models.TextField()),
                ('protocol_label', models.TextField()),
                ('project_name', models.TextField()),
                ('host', models.TextField()),
                ('host_tax_id', models.TextField()),
                ('host_status', models.TextField()),
                ('host_sex', models.TextField()),
                ('submitted_host_sex', models.TextField()),
                ('host_body_site', models.TextField()),
                ('host_gravidity', models.TextField()),
                ('host_phenotype', models.TextField()),
                ('host_genotype', models.TextField()),
                ('host_growth_conditions', models.TextField()),
                ('environmental_package', models.TextField()),
                ('investigation_type', models.TextField()),
                ('experimental_factor', models.TextField()),
                ('sample_collection', models.TextField()),
                ('sequencing_method', models.TextField()),
                ('target_gene', models.TextField()),
                ('ph', models.TextField()),
                ('broker_name', models.TextField()),
            ],
        ),
    ]
