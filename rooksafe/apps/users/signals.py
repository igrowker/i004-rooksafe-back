from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Wallet, User

@receiver(post_save, sender=User)
def create_wallet_for_user(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
