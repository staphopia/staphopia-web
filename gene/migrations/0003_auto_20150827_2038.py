# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0003_auto_20150506_2138'),
        ('analysis', '0018_auto_20150715_1758'),
        ('gene', '0002_auto_20150821_1917'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contigs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(db_index=True)),
                ('sequence', models.TextField()),
                ('sample', models.ForeignKey(to='samples.Sample')),
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
                ('sample', models.ForeignKey(to='samples.Sample')),
                ('version', models.ForeignKey(to='analysis.PipelineVersion')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='annotation',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='cluster',
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='contig',
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='sample',
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='version',
        ),
        migrations.DeleteModel(
            name='Annotation',
        ),
        migrations.AlterUniqueTogether(
            name='features',
            unique_together=set([('sample', 'version', 'cluster')]),
        ),
        migrations.AlterUniqueTogether(
            name='contigs',
            unique_together=set([('sample', 'name')]),
        ),
    ]
