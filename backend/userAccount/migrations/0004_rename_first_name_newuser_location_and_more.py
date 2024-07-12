# Generated by Django 5.0 on 2024-02-07 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userAccount', '0003_alter_newuser_phone_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='newuser',
            old_name='first_name',
            new_name='location',
        ),
        migrations.RemoveField(
            model_name='newuser',
            name='about',
        ),
        migrations.AlterField(
            model_name='newuser',
            name='phone_number',
            field=models.CharField(blank=True, default='0000000000', max_length=20),
        ),
    ]