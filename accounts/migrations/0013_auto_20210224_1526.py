# Generated by Django 3.1.1 on 2021-02-24 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20210224_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobrec',
            name='joblocation',
            field=models.CharField(default='null', max_length=200),
        ),
    ]