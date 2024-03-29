# Generated by Django 3.2.15 on 2022-11-07 15:29

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(default='', max_length=100)),
                ('title', models.CharField(default='', max_length=200)),
                ('subtitle', models.CharField(default='', max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('Sanitary Kits', 'Sanitary Kits'), ('Contraceptives', 'Contraceptives'), ('Fashion', 'Fashion'), ('Others', 'Others')], default='Sanitary Kits', max_length=100)),
                ('size', models.CharField(choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large'), ('Extra Large', 'Extra Large')], default='Medium', max_length=200)),
                ('duration', models.IntegerField(default=30)),
                ('initial_stock', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('current_stock', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('price', models.DecimalField(decimal_places=2, default=100.0, max_digits=9)),
                ('discount', models.DecimalField(decimal_places=2, default=1.0, max_digits=9)),
                ('payment_plan_acceptance_option', models.CharField(max_length=200)),
                ('slug', models.SlugField(editable=False, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('approved', models.BooleanField(default=False)),
                ('featured', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=200)),
                ('rating', models.IntegerField()),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ratingproduct', to='product.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCountViews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField(null=True)),
                ('session', models.CharField(max_length=100, null=True)),
                ('slug', models.SlugField(null=True)),
                ('view_counts', models.IntegerField(default=None)),
                ('product', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_type', models.CharField(choices=[('Image', 'Image'), ('Video', 'Video')], default='Image', max_length=200)),
                ('file', models.FileField(null=True, upload_to='myfairy/product_attachments')),
                ('product', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
    ]
