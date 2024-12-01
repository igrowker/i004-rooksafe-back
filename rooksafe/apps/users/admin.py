from django.contrib import admin
from .models import User, Wallet, Simulation, Transaction, Asset

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'experience_level', 'is_staff', 'is_superuser', 'is_active', 'created_at', 'updated_at')
    list_filter = ('experience_level', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('id',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')

class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__name', 'user__email')


class SimulationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet', 'investment_amount', 'asset_type', 'status', 'created_at')
    list_filter = ('asset_type', 'status', 'created_at')
    search_fields = ('user__name', 'user__email', 'asset_type')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'type', 'amount', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('wallet__user__name', 'wallet__user__email')


class AssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'asset_type', 'current_value', 'previous_value', 'market_cap', 'volume', 'is_active', 'created_at', 'updated_at')
    list_filter = ('asset_type', 'is_active', 'created_at')
    search_fields = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Simulation, SimulationAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Asset, AssetAdmin)
