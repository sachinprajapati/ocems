# Generated by Django 2.2 on 2019-09-23 16:09

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Flats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tower', models.PositiveIntegerField()),
                ('flat', models.PositiveIntegerField()),
                ('owner', models.CharField(blank=True, max_length=255, null=True)),
                ('flat_size', models.PositiveIntegerField()),
                ('profession', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.PositiveIntegerField(choices=[(1, 'Occupied'), (2, 'Vacant')], default=1)),
                ('phone', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 10 digits allowed.", regex='^(\\+\\d{1,3})?,?\\s?\\d{10}')])),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('meter_sr', models.TextField(blank=True, null=True)),
                ('basis', models.PositiveIntegerField(blank=True, choices=[(1, 'N'), (2, 'Y')], null=True)),
                ('fixed_amt', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sno', models.PositiveIntegerField(blank=True, null=True)),
                ('amt_left', models.FloatField(default=0, verbose_name='Amount Left')),
                ('recharge', models.PositiveIntegerField()),
                ('Type', models.PositiveIntegerField(blank=True, choices=[(1, 'cash'), (2, 'bank')], null=True)),
                ('chq_dd', models.PositiveIntegerField(blank=True, null=True)),
                ('eb', models.FloatField(default=0, verbose_name='Utility KWH')),
                ('dg', models.FloatField(default=0, verbose_name='DG KWH')),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Flats')),
            ],
        ),
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eb', models.FloatField(default=0, verbose_name='Utility KWH')),
                ('dg', models.FloatField(default=0, verbose_name='DG KWH')),
                ('ref_eb', models.FloatField(default=0, verbose_name='Ref Utility KWH')),
                ('ref_dg', models.FloatField(default=0, verbose_name='Ref DG KWH')),
                ('eb_price', models.FloatField(default=0, verbose_name='Utility Rate')),
                ('dg_price', models.FloatField(default=0, verbose_name='DG Rate')),
                ('mrate', models.FloatField(verbose_name='Maintance Rate')),
                ('famt', models.FloatField(verbose_name='Fixed Amount')),
                ('amt_left', models.FloatField()),
                ('dt', models.DateTimeField()),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Flats')),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyBill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Bill_Pkey', models.PositiveIntegerField()),
                ('month', models.PositiveIntegerField()),
                ('year', models.PositiveIntegerField()),
                ('start_eb', models.FloatField(default=0, verbose_name='Start Utility KWH')),
                ('start_dg', models.FloatField(default=0, verbose_name='Start DG KWH')),
                ('end_eb', models.FloatField(default=0, verbose_name='End Utility KWH')),
                ('end_dg', models.FloatField(default=0, verbose_name='End DG KWH')),
                ('opn_amt', models.FloatField(default=0, verbose_name='Opening Amount')),
                ('cls_amt', models.FloatField(default=0, verbose_name='Closing Amount')),
                ('eb_price', models.FloatField(default=0, verbose_name='Utility Rate')),
                ('dg_price', models.FloatField(default=0, verbose_name='DG Rate')),
                ('start_dt', models.DateTimeField()),
                ('end_dt', models.DateTimeField(blank=True, null=True)),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Flats')),
            ],
        ),
        migrations.CreateModel(
            name='Maintance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sno', models.PositiveIntegerField()),
                ('Date', models.DateTimeField()),
                ('mrate', models.FloatField(verbose_name='Maintance Rate')),
                ('flat_size', models.PositiveIntegerField()),
                ('mcharge', models.FloatField(verbose_name='Maintance Charges')),
                ('famt', models.FloatField(verbose_name='Fixed Amount')),
                ('field_amt', models.FloatField()),
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
                ('reset_dt', models.DateTimeField(blank=True, null=True)),
                ('meter_change_dt', models.DateTimeField(blank=True, null=True)),
                ('last_modified', models.CharField(max_length=5)),
                ('last_deduction_dt', models.DateTimeField()),
                ('deduction_status', models.PositiveIntegerField(blank=True, choices=[(1, 'N'), (2, 'Y')], null=True)),
                ('ng_eb', models.FloatField(default=0, verbose_name='Negative Utility KWH')),
                ('ng_dg', models.FloatField(default=0, verbose_name='Negative DG KWH')),
                ('ng_dt', models.DateTimeField(blank=True, null=True)),
                ('flat', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.Flats')),
            ],
        ),
    ]
