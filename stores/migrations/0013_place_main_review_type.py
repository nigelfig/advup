# Generated by Django 2.2 on 2020-07-27 19:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0004_reviewlink'),
        ('stores', '0012_auto_20200727_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='main_review_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='links.ReviewLinkType'),
        ),
    ]