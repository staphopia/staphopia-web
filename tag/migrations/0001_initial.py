# Generated by Django 2.0 on 2017-12-13 03:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sample', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.TextField(db_index=True)),
                ('comment', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ToSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_sample', to='sample.Sample')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tag.Tag')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('user', 'tag')},
        ),
    ]
