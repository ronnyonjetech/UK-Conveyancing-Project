# Generated by Django 5.0 on 2024-04-16 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdf_module', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conveyance',
            name='extracted_text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='conveyance',
            name='summarized_text',
            field=models.TextField(blank=True),
        ),
    ]