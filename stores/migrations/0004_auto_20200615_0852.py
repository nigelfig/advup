# Generated by Django 2.2 on 2020-06-15 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0003_place_monthly_sub_uploads_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='total_links',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='place',
            name='total_links_limit',
            field=models.IntegerField(default=100),
        ),
    ]
