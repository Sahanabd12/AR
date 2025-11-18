from django.db import models
import uuid
import os

def get_mind_filename(instance, filename):
    ext = filename.split('.')[-1]
    return f"minds/{instance.original_name}.{ext}"

class Trigger(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    original_name = models.CharField(max_length=255, blank=True)  # NEW
    image = models.ImageField(upload_to='markers/')
    video = models.FileField(upload_to='videos/')
    mind_file = models.FileField(upload_to=get_mind_filename, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Card {self.original_name or self.uid}"