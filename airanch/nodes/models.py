import re
import uuid
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .tasks import create_tunnel_port, delete_tunnel_port_objects, update_pub_key
from django.core.exceptions import ValidationError
import base64
import binascii
from django.conf import settings

# State choices
STATE_CHOICES = [
    ('PENDING', 'Pending'),
    ('READY', 'Ready'),
    ('FAILED', 'Failed'),
]

class Template(models.Model):
    html = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=16, unique=True)

class Node(models.Model):
    name_validator = RegexValidator(
        regex='^[a-z0-9_]*$',
        message='Name must be in lowercase, underscores, and numbers only',
        code='invalid_name'
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='nodes')
    name = models.CharField(max_length=16, unique=True, validators=[name_validator], help_text='Enter a name (lowercase and underscores only).')
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='PENDING')
    os_user_id = models.UUIDField(blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, blank=True, null=True, related_name='nodes')
    error_logs = models.JSONField(default=list, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.name = "".join(re.findall(r'[a-z0-9]+', self.name.lower()))
        super(Node, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

def validate_ssh_public_key(value):
    """
    Validates that the value is a valid SSH public key.
    """
    try:
        parts = value.strip().split()
        if len(parts) < 2 or len(parts) > 3:
            raise ValidationError("Invalid SSH public key format.")

        key_type, key_string = parts[0], parts[1]
        if key_type not in ["ssh-rsa", "ssh-ed25519", "ecdsa-sha2-nistp256"]:
            raise ValidationError("Unsupported SSH key type.")

        # Try decoding the key string
        decoded_key = base64.b64decode(key_string)
    except binascii.Error:
        raise ValidationError("Invalid base64 encoding in SSH public key.")
    except ValueError as e:
        raise ValidationError(f"Invalid SSH public key: {e}")


class PublicKey(models.Model):
    key = models.TextField(validators=[validate_ssh_public_key])
    node = models.OneToOneField('Node', on_delete=models.CASCADE, related_name='pubkey')

    def clean(self):
        validate_ssh_public_key(self.key)

@receiver(post_save, sender=PublicKey)
def trigger_pubkey_post_save(sender, instance, **kwargs):
    update_pub_key.delay(instance.id)

class Port(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='ports')
    entry_port = models.IntegerField(validators=[MinValueValidator(8000)])
    exit_port = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(8000)])
    port_app_id = models.UUIDField(blank=True, null=True)

    def __str__(self):
        return f"Port {self.entry_port} for Node {self.node.name}"

@receiver(post_save, sender=Node)
def trigger_node_post_save(sender, instance, created, **kwargs):
    if created: create_tunnel_port.delay(instance.id)

@receiver(post_delete, sender=Node)
def trigger_node_post_delete(sender, instance, **kwargs):
    delete_tunnel_port_objects.delay(
        instance.os_user_id, 
        instance.node_domain_id
    )
