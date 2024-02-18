import re
import uuid
from django.db import models
from django.core.validators import MinValueValidator
from .tasks import create_tunnel_port
from django.db.models.signals import post_save
from django.dispatch import receiver

# Choices for application type
APPLICATION_TYPES = [
    ('ollama', 'Ollama'),
    ('stable_diffusion', 'Stable Diffusion'),
    ('mimic3', 'Mimic3'),
    ('custom', 'Custom'),  # Added custom application type
]

# Default entry ports for the applications
DEFAULT_ENTRY_PORTS = {
    'ollama': 11434,
    'stable_diffusion': 8001,
    'mimic3': 8002,
    'custom': None,
}

STATE_CHOICES = [
    ('PENDING', 'Pending'),
    ('READY', 'Ready'),
    ('FAILED', 'Failed'),
]

class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES)
    exit_port = models.IntegerField()
    entry_port = models.IntegerField(validators=[MinValueValidator(8000)], blank=True, null=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='PENDING')

    os_user_id = models.UUIDField(blank=True, null=True)
    port_app_id = models.UUIDField(blank=True, null=True)
    site_route_id = models.UUIDField(blank=True, null=True)
    node_domain_id = models.UUIDField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.name = "".join(re.findall(r'[a-z0-9]+', self.name.lower()))
        if self.application_type != 'custom':
            self.entry_port = DEFAULT_ENTRY_PORTS.get(self.application_type)
        super(Node, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

@receiver(post_save, sender=Node)
def trigger_node_post_save(sender, instance, **kwargs):
    create_tunnel_port.delay(instance.id)