# Generated by Django 3.1 on 2020-10-09 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobrec', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joblisttable',
            name='company',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
