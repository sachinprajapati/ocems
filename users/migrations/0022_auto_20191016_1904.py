# Generated by Django 2.2 on 2019-10-16 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_auto_20191013_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recharge',
            name='chq_dd',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]