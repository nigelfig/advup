# Generated by Django 2.2 on 2020-07-15 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0006_auto_20200711_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='slug',
            field=models.SlugField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='place',
            name='title',
            field=models.CharField(default='test title', max_length=255),
            preserve_default=False,
        ),
    ]