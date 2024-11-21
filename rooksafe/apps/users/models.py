from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from rest_framework import serializers

# Create your models here.
# Tabla: users
# id: INT (Primary Key)
# name: VARCHAR
# email: VARCHAR (Unique)
# password: VARCHAR
# experience_level: ENUM('básico', 'intermedio', 'avanzado')
# created_at: TIMESTAMP
# updated_at: TIMESTAMP


class UserManager(BaseUserManager):
    def _create_user(self, name, email, password, experience_level, is_staff, is_superuser, **extra_fields):
        user = self.model(
            name=name,
            email=email,
            experience_level=experience_level,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, name, email, password=None, experience_level='básico', **extra_fields):
        return self._create_user(name, email, password, experience_level, False, False, **extra_fields)

    def create_superuser(self, name, email, password=None, experience_level='básico', **extra_fields):
        return self._create_user(name, email, password, experience_level, is_staff=True, is_superuser=True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=64)
    experience_level = models.CharField(max_length=12, choices=[('básico', 'Básico'),('intermedio', 'Intermedio'),('avanzado','Avanzado')], default="básico")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'experience_level']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.name

class UpdateExperienceLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['experience_level']

    def validate_experience_level(self, value):
        if value not in ['básico', 'intermedio', 'avanzado']:
            raise serializers.ValidationError("Invalid experience level. Must be 'básico', 'intermedio', or 'avanzado'.")
        return value