# Generated by Django 5.0 on 2024-04-18 10:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdf_module', '0008_alter_analyzedconveyance_conveyance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analyzedconveyance',
            name='conveyance',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='pdf_module.conveyance'),
        ),
    ]
