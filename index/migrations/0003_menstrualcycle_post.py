# Generated by Django 3.2.8 on 2022-04-27 02:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_remove_user_parent_email_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(blank=True, default='', max_length=100)),
                ('body', models.TextField(blank=True, default='')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='MenstrualCycle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Last_period_date', models.DateField()),
                ('Cycle_average', models.PositiveIntegerField()),
                ('Period_average', models.PositiveIntegerField()),
                ('Start_date', models.DateField()),
                ('End_date', models.DateField()),
                ('cycle_event_date', models.DateField(blank=True, null=True)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
