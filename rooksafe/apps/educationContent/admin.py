from django.contrib import admin
from .models import EducationContent
# Register your models here.

@admin.register(EducationContent)
class EducationContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'level', 'created_at')
    list_filter = ('content_type', 'level', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at' 
