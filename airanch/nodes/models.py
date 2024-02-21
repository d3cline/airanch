import re
import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .tasks import create_tunnel_port, delete_tunnel_port_objects, update_pub_key

# State choices
STATE_CHOICES = [
    ('PENDING', 'Pending'),
    ('READY', 'Ready'),
    ('FAILED', 'Failed'),
]

class PublicKey(models.Model):
    key = models.TextField(blank=True, null=True)

@receiver(post_save, sender=PublicKey)
def trigger_pubkey_post_save(sender, instance, **kwargs):
    update_pub_key.delay(instance, instance.node)

class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=16, unique=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='PENDING')
    template = models.TextField(blank=True, null=True)
    os_user_id = models.UUIDField(blank=True, null=True)
    site_route_id = models.UUIDField(blank=True, null=True)
    node_domain_id = models.UUIDField(blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    pubkey = models.OneToOneField(PublicKey, on_delete=models.CASCADE, related_name='node', blank=True, null=True)

    error_logs = models.JSONField(default=list, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.name = "".join(re.findall(r'[a-z0-9]+', self.name.lower()))
        super(Node, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Port(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='ports')
    entry_port = models.IntegerField(validators=[MinValueValidator(8000)])
    exit_port = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(8000)])
    port_app_id = models.UUIDField(blank=True, null=True)

    def __str__(self):
        return f"Port {self.entry_port} for Node {self.node.name}"

@receiver(post_save, sender=Node)
def trigger_node_post_save(sender, instance, **kwargs):
    create_tunnel_port.delay(instance.id)

@receiver(post_delete, sender=Node)
def trigger_node_post_delete(sender, instance, **kwargs):
    delete_tunnel_port_objects.delay(
        instance.os_user_id, 
        instance.site_route_id, 
        instance.node_domain_id
    )
