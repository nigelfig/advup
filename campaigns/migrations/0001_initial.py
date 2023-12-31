# Generated by Django 2.2 on 2020-06-01 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('audiences', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_name', models.CharField(max_length=50)),
                ('campaign_sms', models.TextField(max_length=160)),
                ('campaign_link', models.CharField(blank=True, default='', max_length=100)),
                ('create_date', models.DateTimeField()),
                ('audience_size', models.IntegerField()),
                ('successful_sends', models.IntegerField()),
                ('failed_sends', models.IntegerField()),
                ('audience', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audiences.Audience')),
            ],
        ),
    ]
