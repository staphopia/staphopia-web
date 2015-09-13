# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('variant', '0001_initial'),
        ('sample', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterMembers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member', models.TextField(unique=True)),
                ('entry_name', models.TextField()),
                ('length', models.PositiveIntegerField()),
                ('is_rep', models.BooleanField()),
                ('is_seed', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Clusters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('aa', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Contigs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(db_index=True)),
                ('sequence', models.TextField()),
                ('sample', models.ForeignKey(to='sample.MetaData')),
            ],
        ),
        migrations.CreateModel(
            name='Features',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.PositiveIntegerField()),
                ('end', models.PositiveIntegerField()),
                ('is_positive', models.BooleanField()),
                ('is_tRNA', models.BooleanField()),
                ('phase', models.PositiveSmallIntegerField()),
                ('dna', models.TextField()),
                ('aa', models.TextField()),
                ('cluster', models.ForeignKey(to='gene.Clusters')),
                ('contig', models.ForeignKey(to='gene.Contigs')),
                ('sample', models.ForeignKey(to='sample.MetaData')),
            ],
        ),
        migrations.CreateModel(
            name='Names',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('taxon_id', models.PositiveIntegerField()),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='References',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dna', models.TextField()),
                ('aa', models.TextField()),
                ('annotation', models.ForeignKey(to='variant.Annotation')),
                ('cluster', models.ForeignKey(to='gene.Clusters')),
                ('reference', models.ForeignKey(to='variant.Reference')),
            ],
        ),
        migrations.AddField(
            model_name='clustermembers',
            name='cluster',
            field=models.ForeignKey(to='gene.Clusters'),
        ),
        migrations.AddField(
            model_name='clustermembers',
            name='gene',
            field=models.ForeignKey(related_name='gene', to='gene.Names'),
        ),
        migrations.AddField(
            model_name='clustermembers',
            name='organism',
            field=models.ForeignKey(to='gene.Organism'),
        ),
        migrations.AddField(
            model_name='clustermembers',
            name='protein',
            field=models.ForeignKey(related_name='product', to='gene.Names'),
        ),
        migrations.AlterUniqueTogether(
            name='features',
            unique_together=set([('sample', 'contig', 'cluster', 'start', 'end')]),
        ),
        migrations.AlterUniqueTogether(
            name='contigs',
            unique_together=set([('sample', 'name')]),
        ),
    ]
