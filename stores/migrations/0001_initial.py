# Generated by Django 2.2 on 2020-06-01 21:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placeid', models.CharField(max_length=255)),
                ('placename', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('country', models.CharField(max_length=2)),
                ('review_link', models.CharField(max_length=255)),
                ('review_link_id', models.CharField(max_length=255)),
                ('review_number', models.CharField(default='no number', max_length=20)),
                ('store_number', models.CharField(default='no number listed', max_length=20)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('create_date', models.DateTimeField()),
                ('has_number', models.BooleanField(default=False)),
                ('monthly_sms', models.IntegerField(default=1000)),
                ('monthly_sub_uploads', models.IntegerField(default=1000)),
                ('businessperson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Messaging',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_copy', models.TextField(max_length=160)),
                ('no_match_reply', models.TextField(default='', max_length=160)),
                ('want_feedback', models.BooleanField(default=False)),
                ('feedback_copy', models.TextField(default='', max_length=160)),
                ('positive_feedback_reply', models.TextField(default='', max_length=160)),
                ('negative_feedback_reply', models.TextField(default='', max_length=160)),
                ('place', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stores.Place')),
            ],
        ),
    ]
