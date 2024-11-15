from django.db import models


# Create your models here.
# Tabla: users
# id: INT (Primary Key)
# name: VARCHAR
# email: VARCHAR (Unique)
# password: VARCHAR
# experience_level: ENUM('básico', 'intermedio', 'avanzado')
# created_at: TIMESTAMP
# updated_at: TIMESTAMP

class User(models.Model):
    name = models.CharField(max_length=56)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=16)
    experiencia_level = models.CharField(max_length=12, choices=[('basico', 'Básico'),('intermedio', 'Intermedio'),('avanzado','Avanzado')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Usuarios'