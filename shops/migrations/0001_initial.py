# Generated by Django 2.2 on 2020-08-16 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stores', '0016_placedetail_place_map'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reviewer_name', models.CharField(max_length=100)),
                ('reviewer_photo_url', models.CharField(max_length=500)),
                ('relative_time_description', models.CharField(max_length=100)),
                ('rating', models.IntegerField()),
                ('review_text', models.TextField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.Place')),
            ],
        ),
    ]
