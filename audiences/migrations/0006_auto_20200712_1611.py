# Generated by Django 2.2 on 2020-07-12 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audiences', '0005_auto_20200712_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=15),
            preserve_default=False,
        ),
    ]