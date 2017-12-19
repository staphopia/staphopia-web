# Generated by Django 2.0 on 2017-12-19 04:17

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0003_auto_20171215_2005'),
        ('version', '0001_initial'),
        ('variant', '0004_auto_20171219_0354'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snp_count', models.PositiveIntegerField(default=0)),
                ('indel_count', models.PositiveIntegerField(default=0)),
                ('snp', django.contrib.postgres.fields.jsonb.JSONField()),
                ('indel', django.contrib.postgres.fields.jsonb.JSONField()),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='variant.Reference')),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sample.Sample')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='toindel_version', to='version.Version')),
            ],
        ),
        migrations.RemoveField(
            model_name='counts',
            name='sample',
        ),
        migrations.RemoveField(
            model_name='counts',
            name='version',
        ),
        migrations.AlterUniqueTogether(
            name='toindel',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='toindel',
            name='reference',
        ),
        migrations.RemoveField(
            model_name='toindel',
            name='sample',
        ),
        migrations.RemoveField(
            model_name='toindel',
            name='version',
        ),
        migrations.AlterUniqueTogether(
            name='tosnp',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='tosnp',
            name='reference',
        ),
        migrations.RemoveField(
            model_name='tosnp',
            name='sample',
        ),
        migrations.RemoveField(
            model_name='tosnp',
            name='version',
        ),
        migrations.DeleteModel(
            name='Counts',
        ),
        migrations.DeleteModel(
            name='ToIndel',
        ),
        migrations.DeleteModel(
            name='ToSNP',
        ),
        migrations.AlterUniqueTogether(
            name='variant',
            unique_together={('sample', 'version', 'reference')},
        ),
    ]
