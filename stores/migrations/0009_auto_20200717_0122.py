# Generated by Django 2.2 on 2020-07-17 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0008_remove_place_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='feedback_link',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='place',
            name='feedback_link_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
