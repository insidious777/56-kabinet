# Generated by Django 3.2.6 on 2021-10-22 10:52

from django.db import migrations, models
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0008_menuitem_hq_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='menucategory',
            name='can_order',
            field=models.BooleanField(default=True, verbose_name='Can order'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='hq_image',
            field=imagekit.models.fields.ProcessedImageField(null=True, upload_to='hq_menu_images', verbose_name='High quality image'),
        ),
    ]
