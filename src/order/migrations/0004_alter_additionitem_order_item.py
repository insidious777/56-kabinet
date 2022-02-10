# Generated by Django 3.2.6 on 2021-08-09 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_additionitem_addition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionitem',
            name='order_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addition_items', to='order.orderitem', verbose_name='Order item'),
        ),
    ]
