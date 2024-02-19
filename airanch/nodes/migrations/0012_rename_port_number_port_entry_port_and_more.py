# Generated by Django 5.0.2 on 2024-02-18 23:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0011_remove_node_entry_port_remove_node_exit_port_port'),
    ]

    operations = [
        migrations.RenameField(
            model_name='port',
            old_name='port_number',
            new_name='entry_port',
        ),
        migrations.RemoveField(
            model_name='port',
            name='port_type',
        ),
        migrations.AddField(
            model_name='port',
            name='exit_port',
            field=models.IntegerField(default=8000, validators=[django.core.validators.MinValueValidator(8000)]),
            preserve_default=False,
        ),
    ]