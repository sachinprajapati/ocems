# Generated by Django 2.2.5 on 2019-10-11 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20191009_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetemplate',
            name='m_type',
            field=models.PositiveIntegerField(choices=[(1, 'Recharge'), (2, 'Low Balance'), (3, 'Negative Balance'), (4, 'Compose')], unique=True),
        ),
        migrations.CreateModel(
            name='Debit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amt_left', models.DecimalField(decimal_places=4, max_digits=19)),
                ('debit_amt', models.PositiveIntegerField()),
                ('eb', models.DecimalField(decimal_places=4, max_digits=19, verbose_name='Utility KWH')),
                ('dg', models.DecimalField(decimal_places=4, max_digits=19, verbose_name='DG KWH')),
                ('remarks', models.TextField(null=True)),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Flats')),
            ],
        ),
    ]
