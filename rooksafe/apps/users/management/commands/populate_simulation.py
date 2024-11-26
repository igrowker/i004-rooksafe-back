from django.core.management.base import BaseCommand
from faker import Faker
import random
from apps.users.models import Simulation, Asset
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with fake data for simulations and assets'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # usuarios
        for _ in range(10):
            user = User.objects.create_user(
                name=fake.user_name(),
                password='1234', # contraseña de pruebas en production cambiar por ---> password=fake.password()
                email=fake.email(),
            )

            # simulaciones
            for _ in range(5):
                investment_amount = round(random.uniform(1000, 100000), 2)
                asset_type = random.choice(['stock', 'crypto', 'commodity', 'forex'])

                simulation = Simulation.objects.create(
                    user=user,
                    investment_amount=investment_amount,
                    asset_type=asset_type,
                    performance_data={
                        'initial_investment': investment_amount,
                        'current_value': investment_amount,
                        'fluctuations': [round(random.uniform(-0.1, 0.1), 2) for _ in range(10)]
                    }
                )
                simulation.save()

        # activos
        for _ in range(20):
            name = fake.company() if random.choice(['stock', 'crypto', 'commodity', 'forex']) == 'stock' else fake.word()
            asset = Asset.objects.create(
                name=name,
                asset_type=random.choice(['stock', 'crypto', 'commodity', 'forex']),
                current_value=round(random.uniform(10, 10000), 2),
                previous_value=round(random.uniform(10, 10000), 2),
                market_cap=round(random.uniform(100000, 10000000), 2),
                volume=round(random.uniform(1000, 1000000), 2)
            )
            asset.save()

        self.stdout.write(self.style.SUCCESS('Database populated with fake data successfully'))
