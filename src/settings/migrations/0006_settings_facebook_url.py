# Generated by Django 3.2.6 on 2021-10-22 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0005_alter_settings_notify_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='facebook_url',
            field=models.URLField(default='https://www.facebook.com/', verbose_name='Facebook URL'),
        ),
    ]
