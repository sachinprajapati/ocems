# Generated by Django 2.2 on 2020-10-16 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_notice_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complaint',
            name='flat',
        ),
        migrations.DeleteModel(
            name='Notice',
        ),
        migrations.DeleteModel(
            name='Complaint',
        ),
    ]