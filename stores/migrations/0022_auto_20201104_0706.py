# Generated by Django 2.2 on 2020-11-04 07:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0021_auto_20201015_1917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messaging',
            name='negative_feedback_reply',
        ),
        migrations.RemoveField(
            model_name='messaging',
            name='positive_feedback_reply',
        ),
    ]