# Generated by Django 2.2 on 2020-08-17 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0019_placedetail_unformatted_store_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placedetail',
            name='website',
            field=models.CharField(max_length=500),
        ),
    ]