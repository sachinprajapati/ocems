# Generated by Django 2.2.5 on 2019-11-12 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_auto_20191019_0013'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherMaintance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255)),
                ('start_dt', models.DateField()),
                ('end_dt', models.DateField(blank=True, null=True)),
            ],
        ),
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
