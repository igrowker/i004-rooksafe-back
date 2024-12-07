from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import serializers


class UserManager(BaseUserManager):
    def _create_user(self, name, email, password, experience_level, is_staff, is_superuser, **extra_fields):
        extra_fields.setdefault("is_active", True)
        user = self.model(
            name=name,
            email=email,
            experience_level=experience_level,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_user(self, name, email, password=None, experience_level='básico', **extra_fields):
        return self._create_user(name, email, password, experience_level, False, False, **extra_fields)

    def create_superuser(self, name, email, password=None, experience_level='básico', **extra_fields):
        return self._create_user(name, email, password, experience_level, is_staff=True, is_superuser=True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=250)
    experience_level = models.CharField(max_length=12, choices=[('básico', 'Básico'),('intermedio', 'Intermedio'),('avanzado','Avanzado')], default="básico")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('name', )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.name

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=50, choices=[
        ("investment", "Investment"),
        ("withdrawal", "Withdrawal"),
        ("buy", "Buy"),
        ("sell", "Sell")
    ])
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pending"),
        ("completed", "Completed"),
    ], default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Transaction amount must be positive.")

class UpdateExperienceLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['experience_level']

    def validate_experience_level(self, value):
        if value not in ['básico', 'intermedio', 'avanzado']:
            raise serializers.ValidationError("Invalid experience level. Must be 'básico', 'intermedio', or 'avanzado'.")
        return value

class StockInvestment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=10)  # Stock symbol (e.g., 'AAPL')
    number_of_shares = models.FloatField()  # Number of shares the user owns
    purchase_price = models.FloatField()  # The price at which the stock was bought
    current_value = models.FloatField(default=0)  # Current value of the stock (calculated)

    def __str__(self):
        return f"{self.user.username} - {self.stock_symbol}"
    

class StockSaleHistory(models.Model):
    investment = models.ForeignKey(StockInvestment, on_delete=models.CASCADE, related_name="sales_history")
    shares_sold = models.FloatField()  # Number of shares sold
    sale_price = models.FloatField()  # Price at which the stock was sold
    total_value = models.FloatField()  # Total value of the transaction (shares_sold * sale_price)
    sale_date = models.DateTimeField(auto_now_add=True)  # Date of sale

    def __str__(self):
        return f"Sale of {self.shares_sold} shares of {self.investment.stock_symbol} by {self.investment.user.name}"


class StockPurchaseHistory(models.Model):
    investment = models.ForeignKey(StockInvestment, on_delete=models.CASCADE, related_name="purchase_history")
    shares_purchased = models.FloatField()
    sale_price = models.FloatField() 
    total_value = models.FloatField() 
    sale_date = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Purchase of {self.shares_purchased} shares of {self.investment.stock_symbol} by {self.investment.user.name}"
