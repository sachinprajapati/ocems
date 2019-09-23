# Generated by Django 2.2.4 on 2019-09-22 14:30

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20190922_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recharge',
            name='dt',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 22, 14, 30, 36, 992638, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='recharge',
            name='sno',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
