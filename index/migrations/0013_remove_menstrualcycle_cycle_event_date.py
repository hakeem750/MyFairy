# Generated by Django 3.2.8 on 2022-06-27 09:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0012_auto_20220618_1049'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menstrualcycle',
            name='cycle_event_date',
        ),
    ]
