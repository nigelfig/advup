# Generated by Django 2.2 on 2020-06-01 21:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Audience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audience_name', models.CharField(max_length=50)),
                ('create_date', models.DateTimeField()),
                ('businessperson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.Place')),
            ],
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=12)),
                ('definitely_cell_number', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=15)),
                ('last_name', models.CharField(max_length=15)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('audience', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audiences.Audience')),
            ],
        ),
        migrations.CreateModel(
            name='GlobalUnsubscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unsubscriber_number', models.CharField(max_length=12)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.Place')),
            ],
        ),
    ]
