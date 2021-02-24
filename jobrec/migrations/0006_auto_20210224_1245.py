# Generated by Django 3.1.1 on 2021-02-24 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobrec', '0005_auto_20210222_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='advertiserurl',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='jobs',
            name='company',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='jobs',
            name='joblocation',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='jobs',
            name='jobstatus',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]