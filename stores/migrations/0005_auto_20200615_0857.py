# Generated by Django 2.2 on 2020-06-15 08:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0004_auto_20200615_0852'),
    ]

    operations = [
        migrations.RenameField(
            model_name='place',
            old_name='total_links',
            new_name='total_links_remaining',
        ),
    ]
