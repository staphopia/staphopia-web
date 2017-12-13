# Generated by Django 2.0 on 2017-12-13 03:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sample', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(db_index=True)),
                ('sequence', models.TextField()),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plasmid_contig_sample', to='sample.Sample')),
            ],
        ),
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_contig', models.PositiveSmallIntegerField()),
                ('total_contig_length', models.PositiveIntegerField()),
                ('min_contig_length', models.PositiveIntegerField()),
                ('median_contig_length', models.PositiveIntegerField()),
                ('mean_contig_length', models.DecimalField(decimal_places=2, max_digits=9)),
                ('max_contig_length', models.PositiveIntegerField()),
                ('n50_contig_length', models.PositiveIntegerField(default=0)),
                ('l50_contig_count', models.PositiveSmallIntegerField(default=0)),
                ('ng50_contig_length', models.PositiveIntegerField(default=0)),
                ('lg50_contig_count', models.PositiveSmallIntegerField(default=0)),
                ('contigs_greater_1k', models.PositiveSmallIntegerField()),
                ('contigs_greater_10k', models.PositiveSmallIntegerField()),
                ('contigs_greater_100k', models.PositiveSmallIntegerField()),
                ('contigs_greater_1m', models.PositiveSmallIntegerField()),
                ('percent_contigs_greater_1k', models.DecimalField(decimal_places=2, max_digits=5)),
                ('percent_contigs_greater_10k', models.DecimalField(decimal_places=2, max_digits=5)),
                ('percent_contigs_greater_100k', models.DecimalField(decimal_places=2, max_digits=5)),
                ('percent_contigs_greater_1m', models.DecimalField(decimal_places=2, max_digits=5)),
                ('contig_percent_a', models.DecimalField(decimal_places=2, max_digits=5)),
                ('contig_percent_t', models.DecimalField(decimal_places=2, max_digits=5)),
                ('contig_percent_g', models.DecimalField(decimal_places=2, max_digits=5)),
                ('contig_percent_c', models.DecimalField(decimal_places=2, max_digits=5)),
                ('contig_percent_n', models.DecimalField(decimal_places=2, max_digits=5)),
                ('contig_non_acgtn', models.DecimalField(decimal_places=2, max_digits=5)),
                ('num_contig_non_acgtn', models.PositiveSmallIntegerField()),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plasmid_summary_sample', to='sample.Sample')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='contig',
            unique_together={('sample', 'name')},
        ),
    ]
