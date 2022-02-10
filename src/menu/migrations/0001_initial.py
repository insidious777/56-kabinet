# Generated by Django 3.2.6 on 2021-08-07 08:54

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100, verbose_name='Name')),
                ('image', models.ImageField(upload_to='action_images', verbose_name='Image')),
                ('show', models.BooleanField(default=True, verbose_name='Show')),
                ('order_index', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Order index')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Action',
                'verbose_name_plural': 'Actions',
            },
        ),
        migrations.CreateModel(
            name='Addition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('price', models.DecimalField(decimal_places=0, max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Price')),
                ('show', models.BooleanField(default=True, verbose_name='Show')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Addition',
                'verbose_name_plural': 'Additions',
            },
        ),
        migrations.CreateModel(
            name='MenuCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.ImageField(upload_to='menu_category_icons', verbose_name='Icon')),
                ('name', models.CharField(max_length=100, verbose_name='Category name')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('show', models.BooleanField(default=True, verbose_name='Show')),
                ('order_index', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Order index')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Menu category',
                'verbose_name_plural': 'Menu categories',
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='menu_images', verbose_name='Image')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('price', models.DecimalField(decimal_places=0, max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Price')),
                ('volume', models.CharField(blank=True, max_length=50, null=True, verbose_name='Volume')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('show', models.BooleanField(default=True, verbose_name='Show')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='menu_items', to='menu.menucategory', verbose_name='Category')),
                ('possible_additions', models.ManyToManyField(related_name='purpose_menu_items', to='menu.Addition', verbose_name='Possible additions')),
            ],
            options={
                'verbose_name': 'Menu item',
                'verbose_name_plural': 'Menu items',
            },
        ),
    ]
