import sys
import os
import django
from django.contrib.auth import get_user_model
from faker import Faker
import random
from django.utils import timezone



# Añadir la raíz del proyecto a sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Configurar el módulo de settings para Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_app.settings.local')



django.setup()

fake = Faker()

def generate_fake_data(n_users=10, n_simulations=10):
    User = get_user_model() 

    # Generar usuarios falsos
    users = []
    for _ in range(n_users):
        experience_level = random.choice(['básico', 'intermedio', 'avanzado'])

        # Crear el usuario
        user = User(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(length=12),
            experience=experience_level,  
            is_active=True,  
            is_staff=False,  
            is_superuser=False,
            created_at=fake.timezone(),  
            updated_at=fake.timezone(),  
        ) 
        user.last_login = timezone.now()
        user.save()  # Guardamos el usuario
        users.append(user)
    
    
    print("Archivo ejecutado correctamente.")   
    print(f"{n_users} usuarios generados exitosamente.")
    


generate_fake_data()
print("salgo")
