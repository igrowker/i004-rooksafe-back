from django.contrib import admin
from .models import EducationContent

# Register your models here.
@admin.register(EducationContent)
class EducationContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'level', 'image_url','content_url', 'created_at')  # Include image_url
    list_filter = ('content_type', 'level', 'created_at')
    search_fields = ('title', 'content_url', 'image_url')  # Allow searching by image_url and content_url
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
