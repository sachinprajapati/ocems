# Generated by Django 2.2 on 2019-10-05 07:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20191001_2117'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feeder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ps_key', models.PositiveIntegerField(choices=[(1, 'PS2'), (2, 'PS1')])),
                ('name', models.CharField(max_length=255)),
                ('desc', models.TextField(null=True)),
                ('eb', models.DecimalField(decimal_places=4, max_digits=19, null=True, verbose_name='Utility KWH')),
                ('dg', models.DecimalField(decimal_places=4, max_digits=19, null=True, verbose_name='DG KWH')),
                ('load', models.DecimalField(decimal_places=4, max_digits=19, null=True, verbose_name='Running Load')),
                ('f_type', models.PositiveIntegerField(blank=True, choices=[(1, 'Incoming'), (2, 'Outgoing')], null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='recharge',
            name='Type',
            field=models.PositiveIntegerField(blank=True, choices=[(1, 'cash'), (2, 'bank'), (3, 'neft')], null=True),
        ),
        migrations.CreateModel(
            name='FeederReadings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('eb', models.DecimalField(decimal_places=4, max_digits=19, verbose_name='Utility KWH')),
                ('dg', models.DecimalField(decimal_places=4, max_digits=19, verbose_name='DG KWH')),
                ('load', models.DecimalField(decimal_places=4, max_digits=19, verbose_name='Running Load')),
                ('feeder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Feeder')),
            ],
        ),
    ]