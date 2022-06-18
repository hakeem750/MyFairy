# Generated by Django 3.2.8 on 2022-06-18 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0011_auto_20220617_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menstrualcycle',
            name='Cycle_average',
        ),
        migrations.RemoveField(
            model_name='menstrualcycle',
            name='End_date',
        ),
        migrations.RemoveField(
            model_name='menstrualcycle',
            name='Period_average',
        ),
        migrations.RemoveField(
            model_name='menstrualcycle',
            name='Start_date',
        ),
        migrations.AddField(
            model_name='menstrualcycle',
            name='period_flow',
            field=models.CharField(choices=[('LT', 'light'), ('MD', 'medium'), ('HV', 'heavy')], default='MD', max_length=2),
        ),
    ]
