# Generated by Django 2.2 on 2020-08-17 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0017_auto_20200817_0047'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='placedetail',
            name='unformatted_store_number',
        ),
    ]
