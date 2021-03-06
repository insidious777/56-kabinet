# Generated by Django 3.2.6 on 2021-10-22 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0006_settings_facebook_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='address',
            field=models.CharField(default='м.Тернопіль, вул. Грушевського 1', max_length=64, verbose_name='Address'),
        ),
        migrations.AddField(
            model_name='settings',
            name='address_url',
            field=models.URLField(default='https://www.google.com/maps/place/56+%D0%9A%D0%B0%D0%B1%D1%96%D0%BD%D0%B5%D1%82/@49.5539818,25.5927935,18.37z/data=!4m5!3m4!1s0x4730371f9eb9cfbf:0xa6d7469b36e1629c!8m2!3d49.5539927!4d25.593199', max_length=255, verbose_name='Address URL'),
        ),
    ]
