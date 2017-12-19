# Generated by Django 2.0 on 2017-12-18 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0003_auto_20171215_2005'),
        ('staphopia', '0002_delete_version'),
        ('version', '0001_initial'),
        ('sccmec', '0002_auto_20171216_0536'),
    ]

    operations = [
        migrations.AddField(
            model_name='primers',
            name='version',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='sccmec_primers_version', to='version.Version'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proteins',
            name='version',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='sccmec_proteins_version', to='version.Version'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subtypes',
            name='version',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='sccmec_subtypes_version', to='version.Version'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='primers',
            unique_together={('sample', 'version', 'query')},
        ),
        migrations.AlterUniqueTogether(
            name='proteins',
            unique_together={('sample', 'version', 'query')},
        ),
        migrations.AlterUniqueTogether(
            name='subtypes',
            unique_together={('sample', 'version', 'query')},
        ),
    ]