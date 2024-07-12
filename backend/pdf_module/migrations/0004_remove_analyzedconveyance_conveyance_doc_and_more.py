# Generated by Django 5.0 on 2024-04-16 13:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdf_module', '0003_remove_conveyance_extracted_text_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analyzedconveyance',
            name='conveyance_doc',
        ),
        migrations.AddField(
            model_name='conveyance',
            name='analyzed_doc',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='pdf_module.analyzedconveyance'),
        ),
    ]
