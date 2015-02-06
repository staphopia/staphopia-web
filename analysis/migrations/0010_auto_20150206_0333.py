# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0001_initial'),
        ('analysis', '0009_auto_20150206_0000'),
    ]

    operations = [
        migrations.CreateModel(
            name='MLST',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MLSTBlast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('loci_name', models.CharField(max_length=4)),
                ('loci_id', models.PositiveSmallIntegerField()),
                ('bitscore', models.PositiveSmallIntegerField()),
                ('slen', models.PositiveSmallIntegerField()),
                ('length', models.PositiveSmallIntegerField()),
                ('gaps', models.PositiveSmallIntegerField()),
                ('mismatch', models.PositiveSmallIntegerField()),
                ('pident', models.DecimalField(max_digits=5, decimal_places=2)),
                ('evalue', models.DecimalField(max_digits=7, decimal_places=2)),
                ('mlst', models.ForeignKey(to='analysis.MLST')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MLSTSequenceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ST', models.PositiveIntegerField(unique=True, db_index=True)),
                ('arcc', models.PositiveIntegerField()),
                ('aroe', models.PositiveIntegerField()),
                ('glpf', models.PositiveIntegerField()),
                ('gmk', models.PositiveIntegerField()),
                ('pta', models.PositiveIntegerField()),
                ('tpi', models.PositiveIntegerField()),
                ('yqil', models.PositiveIntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MLSTSrst2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ST', models.TextField()),
                ('arcc', models.TextField()),
                ('aroe', models.TextField()),
                ('glpf', models.TextField()),
                ('gmk', models.TextField()),
                ('pta', models.TextField()),
                ('tpi', models.TextField()),
                ('yqil', models.TextField()),
                ('mismatches', models.TextField()),
                ('uncertainty', models.TextField()),
                ('depth', models.DecimalField(max_digits=8, decimal_places=3)),
                ('maxMAF', models.DecimalField(max_digits=11, decimal_places=7)),
                ('mlst', models.ForeignKey(to='analysis.MLST', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mlstblast',
            unique_together=set([('mlst', 'loci_name', 'loci_id')]),
        ),
        migrations.AddField(
            model_name='mlst',
            name='blast_st',
            field=models.ForeignKey(to='analysis.MLSTSequenceType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mlst',
            name='sample',
            field=models.ForeignKey(to='samples.Sample'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mlst',
            name='version',
            field=models.ForeignKey(to='analysis.PipelineVersion'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='mlst',
            unique_together=set([('sample', 'version')]),
        ),
    ]
