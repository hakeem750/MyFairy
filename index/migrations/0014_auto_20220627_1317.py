# Generated by Django 3.2.8 on 2022-06-27 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0013_remove_menstrualcycle_cycle_event_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='body',
            field=models.TextField(blank=True, default=''),
        ),
    ]
