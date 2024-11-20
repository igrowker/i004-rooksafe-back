from django.db import models

# Create your models here.
from django.db import models

class EducationContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('artículo', 'Artículo'),
        ('podcast', 'Podcast')
    ]
    LEVEL_CHOICES = [
        ('básico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado')
    ]

    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=12, choices=CONTENT_TYPE_CHOICES)
    level = models.CharField(max_length=12, choices=LEVEL_CHOICES)
    content_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.content_type} - {self.level})"
