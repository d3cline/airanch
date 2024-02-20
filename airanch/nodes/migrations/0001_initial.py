# Generated by Django 5.0.2 on 2024-02-20 21:44

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=16, unique=True)),
                ('state', models.CharField(choices=[('PENDING', 'Pending'), ('READY', 'Ready'), ('FAILED', 'Failed')], default='PENDING', max_length=10)),
                ('template', models.TextField(blank=True, null=True)),
                ('os_user_id', models.UUIDField(blank=True, null=True)),
                ('site_route_id', models.UUIDField(blank=True, null=True)),
                ('node_domain_id', models.UUIDField(blank=True, null=True)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('error_logs', models.JSONField(blank=True, default=list, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PublicKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_port', models.IntegerField(validators=[django.core.validators.MinValueValidator(8000)])),
                ('exit_port', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(8000)])),
                ('port_app_id', models.UUIDField(blank=True, null=True)),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ports', to='nodes.node')),
            ],
        ),
        migrations.AddField(
            model_name='node',
            name='pubkey',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='publickey', to='nodes.publickey'),
        ),
    ]
