# Generated by Django 5.0 on 2024-04-18 10:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdf_module', '0010_alter_analyzedconveyance_conveyance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analyzedconveyance',
            name='conveyance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pdf_module.conveyance'),
        ),
    ]
