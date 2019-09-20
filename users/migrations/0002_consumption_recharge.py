# Generated by Django 2.2.5 on 2019-09-20 16:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no', models.PositiveIntegerField()),
                ('amt_left', models.FloatField(default=0, verbose_name='Amount Left')),
                ('recharge', models.PositiveIntegerField()),
                ('Type', models.PositiveIntegerField(blank=True, choices=[(1, 'N'), (2, 'Y')], null=True)),
                ('chq_dd', models.PositiveIntegerField(blank=True, null=True)),
                ('eb', models.FloatField(default=0, verbose_name='Utility KWH')),
                ('dg', models.FloatField(default=0, verbose_name='DG KWH')),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Flats')),
            ],
        ),
        migrations.CreateModel(
            name='Consumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('eb', models.FloatField(default=0, verbose_name='Utility KWH')),
                ('dg', models.FloatField(default=0, verbose_name='DG KWH')),
                ('ref_eb', models.FloatField(default=0, verbose_name='Ref Utility KWH')),
                ('ref_dg', models.FloatField(default=0, verbose_name='Ref DG KWH')),
                ('start_eb', models.FloatField(default=0, verbose_name='Start Utility KWH')),
                ('start_dg', models.FloatField(default=0, verbose_name='Start DG KWH')),
                ('amt_left', models.FloatField(default=0, verbose_name='Amount Left')),
                ('status', models.PositiveIntegerField(blank=True, null=True)),
                ('reset_dt', models.DateTimeField()),
                ('meter_change_dt', models.DateTimeField(blank=True, null=True)),
                ('last_modified', models.CharField(max_length=5)),
                ('last_deduction_dt', models.DateTimeField()),
                ('deduction_status', models.PositiveIntegerField(blank=True, choices=[(1, 'N'), (2, 'Y')], null=True)),
                ('ng_eb', models.FloatField(default=0, verbose_name='Negative Utility KWH')),
                ('ng_dg', models.FloatField(default=0, verbose_name='Negative DG KWH')),
                ('ng_dt', models.DateTimeField(blank=True, null=True)),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Flats')),
            ],
        ),
    ]
