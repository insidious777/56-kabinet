# Generated by Django 3.2.6 on 2021-08-04 11:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_order_completion_time', models.DurationField(default=datetime.timedelta(seconds=1800), verbose_name='Minimum order completion time')),
                ('order_prepayment_start_from', models.DecimalField(decimal_places=0, default='400', help_text='Amount, from which prepayment will be required', max_digits=6, verbose_name='Order prepayment start from')),
                ('prepayment_percent', models.DecimalField(decimal_places=0, default='25', help_text='From total order amount', max_digits=6, verbose_name='Prepayment percent')),
                ('phone_number', models.CharField(default='067 740 00 56', max_length=13, verbose_name='Phone number')),
                ('instagram_url', models.URLField(default='https://www.instagram.com/', verbose_name='Instagram URL')),
                ('work_schedule', models.CharField(default='з 8:00 по 22:00', max_length=100, verbose_name='Work schedule')),
                ('work_schedule_on_weekend', models.CharField(default='з 9:00 по 22:00', max_length=100, verbose_name='Work schedule on weekend')),
                ('delivery_available', models.BooleanField(default=False, verbose_name='Delivery available')),
                ('delivery_time_within_city', models.DurationField(default=datetime.timedelta(seconds=1800), verbose_name='Delivery time within city')),
                ('delivery_time_beyond_city', models.DurationField(default=datetime.timedelta(seconds=3600), verbose_name='Delivery time beyond city')),
                ('delivery_cost', models.DecimalField(decimal_places=0, default='30', max_digits=6, verbose_name='Delivery cost')),
            ],
            options={
                'verbose_name': 'Settings',
                'verbose_name_plural': 'Settings',
            },
        ),
    ]
