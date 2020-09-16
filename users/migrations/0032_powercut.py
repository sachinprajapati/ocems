# Generated by Django 2.2.7 on 2020-09-15 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_deductionamt_set_load'),
    ]

    operations = [
        migrations.CreateModel(
            name='PowerCut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('running_load', models.FloatField()),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Flats')),
            ],
        ),
    ]
