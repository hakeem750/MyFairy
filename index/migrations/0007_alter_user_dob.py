# Generated by Django 3.2 on 2022-05-01 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0006_auto_20220501_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dob',
            field=models.DateField(null=True, verbose_name='Date of Birth'),
        ),
    ]