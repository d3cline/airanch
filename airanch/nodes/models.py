from django.db import models
import uuid

# Choices for application type
APPLICATION_TYPES = [
    ('ollama', 'Ollama'),
    ('stable_diffusion', 'Stable Diffusion'),
    ('mimic3', 'Mimic3'),
]

class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES)
    exit_port = models.IntegerField()

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Node, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
