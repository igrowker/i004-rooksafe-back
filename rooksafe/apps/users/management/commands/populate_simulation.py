from django.core.management.base import BaseCommand
from faker import Faker
import random
from apps.users.models import Simulation, Asset, Wallet
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with fake data for simulations and assets'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create users and their wallets
        for _ in range(10):
            user = User.objects.create_user(
                name=fake.user_name(),
                password='1234',  # Test password; replace with secure logic in production
                email=fake.email(),
            )

            # Check if the user already has a wallet; if not, create one
            wallet, created = Wallet.objects.get_or_create(user=user)
            if created:
                wallet.balance = round(random.uniform(1000, 50000), 2)
                wallet.save()

            # Create simulations linked to the wallet
            for _ in range(5):
                investment_amount = round(random.uniform(1000, 100000), 2)
                asset_type = random.choice(['stock', 'crypto', 'commodity', 'forex'])

                Simulation.objects.create(
                    user=user,
                    wallet=wallet,  # Associate the simulation with the user's wallet
                    investment_amount=investment_amount,
                    asset_type=asset_type,
                    performance_data={
                        'initial_investment': investment_amount,
                        'current_value': investment_amount,
                        'fluctuations': [round(random.uniform(-0.1, 0.1), 2) for _ in range(10)]
                    }
                )

        # Create assets
        for _ in range(20):
            name = fake.company() if random.choice(['stock', 'crypto', 'commodity', 'forex']) == 'stock' else fake.word()
            Asset.objects.create(
                name=name,
                asset_type=random.choice(['stock', 'crypto', 'commodity', 'forex']),
                current_value=round(random.uniform(10, 10000), 2),
                previous_value=round(random.uniform(10, 10000), 2),
                market_cap=round(random.uniform(100000, 10000000), 2),
                volume=round(random.uniform(1000, 1000000), 2)
            )

        self.stdout.write(self.style.SUCCESS('Database populated with fake data successfully'))

