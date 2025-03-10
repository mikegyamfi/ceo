# Generated by Django 4.2.4 on 2025-01-14 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intel_app', '0012_alter_color_color_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mtntransaction',
            name='amount',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='category/'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='product_images/'),
        ),
    ]
