# Generated by Django 2.2.5 on 2019-10-01 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20190929_0009'),
    ]

    operations = [
        migrations.RenameField(
            model_name='consumption',
            old_name='datetime',
            new_name='dt',
        ),
    ]
