# Generated by Django 2.2 on 2019-10-18 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20191016_1904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintance',
            name='dt',
            field=models.DateTimeField(),
        ),
    ]
