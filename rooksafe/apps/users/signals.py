from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Wallet, User, Transaction

# instancia wallet junto con el registro de usuario
@receiver(post_save, sender=User)
def create_wallet_for_user(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

@receiver(post_save, sender=Transaction)
def update_wallet_balance(sender, instance, created, **kwargs):

    if created and instance.status == "completed":
        wallet = instance.wallet
        # investment puede ser add money
        if instance.type in ["investment", "sell"]:
            wallet.balance += instance.amount
        # elif instance.type in ["withdrawal", "buy"]:
        #     wallet.balance -= instance.amount

        wallet.save()