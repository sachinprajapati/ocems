# Generated by Django 2.2 on 2020-10-16 13:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0035_auto_20201016_1918'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub', models.CharField(max_length=255, verbose_name='Subject')),
                ('text', models.TextField()),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Active'), (2, 'Inactive')], default=1)),
                ('dt', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 10 digits allowed.", regex='^(\\+\\d{1,3})?,?\\s?\\d{10}')])),
                ('remark', models.TextField(verbose_name='Remark')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Active'), (2, 'In progress'), (3, 'Closed')], default=1)),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('solved_dt', models.DateTimeField(blank=True, null=True)),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Flats')),
            ],
        ),
    ]
