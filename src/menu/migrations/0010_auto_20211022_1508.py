# Generated by Django 3.2.6 on 2021-10-22 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0009_auto_20211022_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='menucategory',
            name='from_time',
            field=models.TimeField(blank=True, null=True, verbose_name='From hour'),
        ),
        migrations.AddField(
            model_name='menucategory',
            name='to_time',
            field=models.TimeField(blank=True, null=True, verbose_name='To hour'),
        ),
    ]