# Generated by Django 3.1.7 on 2021-03-11 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexinghistory',
            name='elastic_server_ip',
            field=models.CharField(default='127.0.0.1', max_length=20),
        ),
        migrations.AddField(
            model_name='indexinghistory',
            name='elastic_server_port',
            field=models.CharField(default='9200', max_length=10),
        ),
    ]