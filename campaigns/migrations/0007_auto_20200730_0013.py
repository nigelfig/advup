# Generated by Django 2.2 on 2020-07-30 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0006_auto_20200729_2111'),
    ]

    operations = [
        migrations.CreateModel(
            name='CeleryModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('celery_task_id', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='campaign',
            name='celery_task_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='was_scheduled',
            field=models.BooleanField(default=False),
        ),
    ]
