# Generated by Django 2.2.5 on 2019-09-25 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_deductionamt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reading',
            name='dt',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
