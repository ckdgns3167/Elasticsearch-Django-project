# Generated by Django 3.1.7 on 2021-03-18 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_auto_20210311_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indexinghistory',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]