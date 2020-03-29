# Generated by Django 2.2.5 on 2019-10-31 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_auto_20191019_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumption',
            name='status',
            field=models.PositiveIntegerField(blank=True, choices=[(1, 'N'), (2, 'Y')], null=True),
        ),
        migrations.AlterField(
            model_name='monthlybill',
            name='end_dt',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='monthlybill',
            name='start_dt',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
