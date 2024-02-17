# Generated by Django 5.0.2 on 2024-02-14 20:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0003_alter_node_entry_port'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='entry_port',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(8000)]),
        ),
    ]