# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gene', '0003_auto_20150923_1755'),
        ('variant', '0005_snpcounts'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('product', models.TextField()),
                ('dna', models.TextField()),
                ('aa', models.TextField()),
                ('cluster', models.ForeignKey(default=0, to='gene.Clusters')),
            ],
        ),
        migrations.CreateModel(
            name='Genotype',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Phenotype',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('predicted_mic', models.TextField()),
                ('name', models.ForeignKey(to='resistance.Name')),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pmid', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ToSNP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('snp', models.ForeignKey(related_name='resistance_snp', to='variant.SNP')),
            ],
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveIntegerField()),
                ('substitution', models.TextField()),
                ('gene', models.ForeignKey(to='resistance.Gene')),
            ],
        ),
        migrations.AddField(
            model_name='tosnp',
            name='variant',
            field=models.ForeignKey(to='resistance.Variant'),
        ),
        migrations.AddField(
            model_name='phenotype',
            name='publication',
            field=models.ForeignKey(to='resistance.Publication'),
        ),
        migrations.AddField(
            model_name='genotype',
            name='phenotype',
            field=models.ForeignKey(to='resistance.Phenotype'),
        ),
        migrations.AddField(
            model_name='genotype',
            name='variant',
            field=models.ForeignKey(to='resistance.Variant'),
        ),
    ]
