# Generated by Django 4.2.4 on 2025-03-10 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intel_app', '0016_checkertype_resultchecker_resultcheckertransaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admininfo',
            name='ishare_source',
            field=models.CharField(choices=[('Geosams', 'Geosams'), ('Noble', 'Noble')], default='Geosams', max_length=300),
        ),
    ]
