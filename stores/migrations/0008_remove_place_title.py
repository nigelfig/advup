# Generated by Django 2.2 on 2020-07-15 18:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0007_auto_20200715_1733'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='title',
        ),
    ]