# Generated by Django 3.2.6 on 2021-08-09 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_alter_additionitem_order_item'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='additionitem',
            options={'verbose_name': 'Addition item', 'verbose_name_plural': 'Addition items'},
        ),
        migrations.AddField(
            model_name='orderitem',
            name='total_amount',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=6, verbose_name='Total amount'),
        ),
    ]
