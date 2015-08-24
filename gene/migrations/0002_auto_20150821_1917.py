# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gene', '0001_initial'),
        ('samples', '0003_auto_20150506_2138'),
        ('variant', '0001_initial'),
        ('assembly', '0001_initial'),
        ('analysis', '0018_auto_20150715_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='references',
            name='annotation',
            field=models.ForeignKey(to='variant.Annotation'),
        ),
        migrations.AddField(
            model_name='references',
            name='cluster',
            field=models.ForeignKey(to='gene.Clusters'),
        ),
        migrations.AddField(
            model_name='references',
            name='reference',
            field=models.ForeignKey(to='variant.Reference'),
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
        migrations.AddField(
            model_name='annotation',
            name='cluster',
            field=models.ForeignKey(to='gene.Clusters'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='contig',
            field=models.ForeignKey(to='assembly.Contigs'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='sample',
            field=models.ForeignKey(to='samples.Sample'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='version',
            field=models.ForeignKey(to='analysis.PipelineVersion'),
        ),
        migrations.AlterUniqueTogether(
            name='annotation',
            unique_together=set([('sample', 'version', 'cluster')]),
        ),
    ]
