# Generated by Django 2.2 on 2019-09-27 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20190927_1407'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maintance',
            name='flat_size',
        ),
        migrations.RemoveField(
            model_name='maintance',
            name='sno',
        ),
    ]
